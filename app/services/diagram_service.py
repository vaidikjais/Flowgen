"""
Diagram Service - Main Business Logic for Diagram Generation

Orchestrates the complete diagram generation workflow including:
- Cache checking
- LLM generation
- Graphviz rendering
- Database persistence
- Logging
"""
import base64
from typing import Optional, Tuple
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import DiagramGenerationError
from app.repository.diagram_repository import DiagramRepository
from app.repository.generation_log_repository import GenerationLogRepository
from app.services.llm_service import LLMService
from app.services.render_service import RenderService
from app.services.cache_service import CacheService
from app.models.diagram_model import Diagram
from app.schemas.diagram_schema import DiagramCreate
from app.utils.hash_utils import hash_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DiagramService:
    """
    Main service class orchestrating diagram generation workflow.
    
    Coordinates between LLM, rendering, caching, and persistence layers.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize service with database session.
        
        Args:
            db: Async database session
        """
        self.db = db
        self.diagram_repo = DiagramRepository(db)
        self.log_repo = GenerationLogRepository(db)
        self.cache_service = CacheService(db)
        self.llm_service = LLMService()
        self.render_service = RenderService()
    
    async def generate_diagram(
        self,
        prompt: str,
        format: str = "svg",
        layout: str = "dot",
        user_id: Optional[str] = None,
        save_to_db: bool = True
    ) -> Tuple[bytes, str, Optional[UUID]]:
        """
        Generate a diagram from natural language prompt.
        
        Complete workflow:
        1. Check cache for existing diagram
        2. If not cached, call LLM to generate DOT code
        3. Validate and render DOT code to image
        4. Save diagram and log to database
        5. Return rendered image and metadata
        
        Args:
            prompt: Natural language description
            format: Output format (svg or png)
            layout: Graphviz layout engine
            user_id: Optional user identifier
            save_to_db: Whether to save diagram to database
            
        Returns:
            Tuple of (image_bytes, dot_code, diagram_id)
            
        Raises:
            DiagramGenerationError: If generation fails
        """
        start_time = datetime.now(timezone.utc)
        prompt_hash = hash_prompt(prompt, format, layout)
        
        logger.info(f"Generating diagram: prompt='{prompt[:50]}...', format={format}, layout={layout}")
        
        # Step 1: Check cache
        cached_diagram = await self.cache_service.get_cached_diagram(prompt, format, layout)
        
        if cached_diagram:
            logger.info("Using cached diagram")
            
            # Log cache hit
            await self.log_repo.create(
                prompt=prompt,
                prompt_hash=prompt_hash,
                success=True,
                was_cached=True,
                user_id=user_id,
                diagram_id=cached_diagram.id
            )
            
            # Return cached image (re-render or use stored)
            if cached_diagram.image_data:
                # Decode base64 stored image
                image_bytes = base64.b64decode(cached_diagram.image_data)
            else:
                # Re-render from DOT code
                image_bytes = await self.render_service.render_to_bytes(
                    cached_diagram.dot_code,
                    format,
                    layout
                )
            
            return image_bytes, cached_diagram.dot_code, cached_diagram.id
        
        # Step 2: Generate DOT code via LLM
        try:
            dot_code, tokens_used, llm_latency_ms = await self.llm_service.generate_dot_code(
                prompt=prompt,
                max_tokens=settings.MAX_TOKENS
            )
            
            logger.info(f"Generated DOT code ({len(dot_code)} characters)")
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            
            # Log failure
            await self.log_repo.create(
                prompt=prompt,
                prompt_hash=prompt_hash,
                success=False,
                error_message=str(e),
                error_type="LLMError",
                user_id=user_id
            )
            
            raise DiagramGenerationError(
                "Failed to generate diagram from prompt",
                detail=str(e)
            )
        
        # Step 3: Render DOT code to image
        try:
            image_bytes = await self.render_service.render_to_bytes(
                dot=dot_code,
                fmt=format,
                engine=layout
            )
            
            logger.info(f"Rendered diagram ({len(image_bytes)} bytes)")
            
        except Exception as e:
            logger.error(f"Rendering failed: {e}")
            
            # Log failure
            await self.log_repo.create(
                prompt=prompt,
                prompt_hash=prompt_hash,
                success=False,
                tokens_used=tokens_used,
                latency_ms=llm_latency_ms,
                error_message=str(e),
                error_type="RenderError",
                user_id=user_id
            )
            
            raise DiagramGenerationError(
                "Failed to render diagram",
                detail=str(e)
            )
        
        # Step 4: Save to database
        diagram_id = None
        if save_to_db:
            try:
                # Encode image as base64 for storage (optional)
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
                diagram_data = DiagramCreate(
                    prompt=prompt,
                    prompt_hash=prompt_hash,
                    dot_code=dot_code,
                    format=format,
                    layout=layout,
                    image_data=image_base64,
                    user_id=user_id,
                    token_count=tokens_used,
                    generation_time_ms=llm_latency_ms
                )
                
                diagram = await self.diagram_repo.create(diagram_data)
                diagram_id = diagram.id
                
                logger.info(f"Saved diagram to database: {diagram_id}")
                
            except Exception as e:
                logger.error(f"Failed to save diagram: {e}")
                # Don't fail the request, just log the error
        
        # Step 5: Log successful generation
        total_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        await self.log_repo.create(
            prompt=prompt,
            prompt_hash=prompt_hash,
            success=True,
            tokens_used=tokens_used,
            model_used=settings.OPENAI_MODEL,
            latency_ms=llm_latency_ms,
            total_time_ms=total_time_ms,
            was_cached=False,
            user_id=user_id,
            diagram_id=diagram_id
        )
        
        logger.info(
            f"Successfully generated diagram in {total_time_ms}ms "
            f"(LLM: {llm_latency_ms}ms, tokens: {tokens_used})"
        )
        
        return image_bytes, dot_code, diagram_id
    
    async def preview_diagram(
        self,
        dot_code: str,
        format: str = "svg",
        layout: str = "dot"
    ) -> bytes:
        """
        Preview/render DOT code without LLM or database operations.
        
        Args:
            dot_code: Graphviz DOT code
            format: Output format
            layout: Layout engine
            
        Returns:
            Rendered image bytes
            
        Raises:
            DiagramGenerationError: If rendering fails
        """
        logger.info(f"Previewing diagram: format={format}, layout={layout}")
        
        try:
            image_bytes = await self.render_service.render_to_bytes(
                dot=dot_code,
                fmt=format,
                engine=layout
            )
            
            logger.info(f"Preview rendered ({len(image_bytes)} bytes)")
            return image_bytes
            
        except Exception as e:
            logger.error(f"Preview rendering failed: {e}")
            raise DiagramGenerationError(
                "Failed to preview diagram",
                detail=str(e)
            )
    
    async def get_diagram_history(
        self,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> Tuple[list[Diagram], int]:
        """
        Get diagram generation history.
        
        Args:
            limit: Maximum number of diagrams to return
            offset: Number of diagrams to skip
            user_id: Optional user ID filter
            
        Returns:
            Tuple of (diagrams list, total count)
        """
        logger.debug(f"Fetching diagram history: limit={limit}, offset={offset}")
        
        diagrams = await self.diagram_repo.list_all(
            limit=limit,
            offset=offset,
            user_id=user_id
        )
        
        total = await self.diagram_repo.count(user_id=user_id)
        
        return diagrams, total
    
    async def get_diagram_by_id(self, diagram_id: str) -> Optional[Diagram]:
        """
        Get a specific diagram by ID.
        
        Args:
            diagram_id: Diagram UUID as string
            
        Returns:
            Diagram if found, None otherwise
        """
        return await self.diagram_repo.get_by_id(diagram_id)
    
    async def delete_diagram(self, diagram_id: str) -> bool:
        """
        Delete a diagram.
        
        Args:
            diagram_id: Diagram UUID as string
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting diagram: {diagram_id}")
        return await self.diagram_repo.delete(diagram_id)


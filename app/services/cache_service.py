"""
Cache Service - Business Logic for Diagram Caching

Handles caching of generated diagrams to reduce redundant LLM calls.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repository.diagram_repository import DiagramRepository
from app.models.diagram_model import Diagram
from app.utils.hash_utils import hash_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """Service class for diagram caching operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize cache service with database session.
        
        Args:
            db: Async database session
        """
        self.db = db
        self.diagram_repo = DiagramRepository(db)
    
    async def get_cached_diagram(
        self,
        prompt: str,
        format: str,
        layout: str
    ) -> Optional[Diagram]:
        """
        Check if a diagram was previously generated for this prompt.
        
        Args:
            prompt: User prompt
            format: Output format (svg/png)
            layout: Layout engine
            
        Returns:
            Cached diagram if found, None otherwise
        """
        if not settings.ENABLE_CACHE:
            logger.debug("Cache is disabled")
            return None
        
        prompt_hash = hash_prompt(prompt, format, layout)
        
        cached = await self.diagram_repo.find_by_prompt_hash(
            prompt_hash=prompt_hash,
            format=format,
            layout=layout
        )
        
        if cached:
            logger.info(f"Cache hit for prompt: {prompt[:50]}...")
            return cached
        else:
            logger.debug(f"Cache miss for prompt: {prompt[:50]}...")
            return None
    
    async def cache_diagram(
        self,
        diagram: Diagram
    ) -> Diagram:
        """
        Store a diagram in the cache.
        
        Args:
            diagram: Diagram entity to cache
            
        Returns:
            Cached diagram entity
        """
        if not settings.ENABLE_CACHE:
            logger.debug("Cache is disabled, not storing diagram")
            return diagram
        
        logger.info(f"Cached diagram for prompt: {diagram.prompt[:50]}...")
        return diagram


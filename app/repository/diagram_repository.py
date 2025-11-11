"""
Diagram Repository - Data Access Layer for Diagrams

Handles all database operations for diagram entities.
Provides clean abstraction over database interactions.
"""
import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagram_model import Diagram
from app.schemas.diagram_schema import DiagramCreate, DiagramUpdate

logger = logging.getLogger(__name__)


class DiagramRepository:
    """Repository class for diagram database operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def create(self, diagram_data: DiagramCreate) -> Diagram:
        """
        Create a new diagram.
        
        Args:
            diagram_data: Diagram creation data
            
        Returns:
            Created diagram entity
        """
        diagram = Diagram(**diagram_data.model_dump())
        self.db.add(diagram)
        await self.db.commit()
        await self.db.refresh(diagram)
        logger.debug(f"Created diagram: {diagram.id}")
        return diagram
    
    async def get_by_id(self, diagram_id: str) -> Optional[Diagram]:
        """
        Get diagram by ID.
        
        Args:
            diagram_id: Diagram UUID as string
            
        Returns:
            Diagram if found, None otherwise
        """
        try:
            uuid_obj = UUID(diagram_id)
            diagram = await self.db.get(Diagram, uuid_obj)
            return diagram
        except ValueError:
            logger.warning(f"Invalid UUID format: {diagram_id}")
            return None
    
    async def find_by_prompt_hash(
        self,
        prompt_hash: str,
        format: str,
        layout: str
    ) -> Optional[Diagram]:
        """
        Find diagram by prompt hash for cache lookup.
        
        Args:
            prompt_hash: SHA-256 hash of the prompt
            format: Output format
            layout: Layout engine
            
        Returns:
            Cached diagram if found, None otherwise
        """
        statement = select(Diagram).where(
            Diagram.prompt_hash == prompt_hash,
            Diagram.format == format,
            Diagram.layout == layout
        ).order_by(Diagram.created_at.desc())
        
        result = await self.db.execute(statement)
        diagram = result.scalars().first()
        
        if diagram:
            logger.debug(f"Cache hit for prompt_hash: {prompt_hash[:8]}...")
        
        return diagram
    
    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> List[Diagram]:
        """
        List all diagrams with pagination.
        
        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip
            user_id: Optional user ID filter
            
        Returns:
            List of diagrams
        """
        statement = select(Diagram)
        
        if user_id:
            statement = statement.where(Diagram.user_id == user_id)
        
        statement = (
            statement
            .order_by(Diagram.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(statement)
        diagrams = result.scalars().all()
        
        logger.debug(f"Retrieved {len(diagrams)} diagrams")
        return list(diagrams)
    
    async def count(self, user_id: Optional[str] = None) -> int:
        """
        Count total number of diagrams.
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            Total count
        """
        from sqlalchemy import func
        
        statement = select(func.count(Diagram.id))
        
        if user_id:
            statement = statement.where(Diagram.user_id == user_id)
        
        result = await self.db.execute(statement)
        count = result.scalar_one()
        return count
    
    async def update(
        self,
        diagram_id: str,
        diagram_data: DiagramUpdate
    ) -> Optional[Diagram]:
        """
        Update diagram.
        
        Args:
            diagram_id: Diagram UUID as string
            diagram_data: Update data
            
        Returns:
            Updated diagram if found, None otherwise
        """
        diagram = await self.get_by_id(diagram_id)
        if not diagram:
            return None
        
        # Update fields
        update_dict = diagram_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(diagram, key, value)
        
        diagram.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        
        self.db.add(diagram)
        await self.db.commit()
        await self.db.refresh(diagram)
        
        logger.debug(f"Updated diagram: {diagram_id}")
        return diagram
    
    async def delete(self, diagram_id: str) -> bool:
        """
        Delete diagram.
        
        Args:
            diagram_id: Diagram UUID as string
            
        Returns:
            True if deleted, False if not found
        """
        diagram = await self.get_by_id(diagram_id)
        if not diagram:
            return False
        
        await self.db.delete(diagram)
        await self.db.commit()
        
        logger.debug(f"Deleted diagram: {diagram_id}")
        return True
    
    async def delete_old(self, days: int = 30) -> int:
        """
        Delete diagrams older than specified days.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of diagrams deleted
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_date = cutoff_date.replace(tzinfo=None)
        
        statement = select(Diagram).where(Diagram.created_at < cutoff_date)
        result = await self.db.execute(statement)
        old_diagrams = result.scalars().all()
        
        count = len(old_diagrams)
        
        for diagram in old_diagrams:
            await self.db.delete(diagram)
        
        await self.db.commit()
        
        logger.info(f"Deleted {count} old diagrams (older than {days} days)")
        return count


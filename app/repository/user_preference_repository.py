"""
User Preference Repository - Data Access Layer for User Preferences

Handles all database operations for user preference entities.
"""
import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_preference_model import UserPreference
from app.schemas.user_preference_schema import (
    UserPreferenceCreate,
    UserPreferenceUpdate
)

logger = logging.getLogger(__name__)


class UserPreferenceRepository:
    """Repository class for user preference database operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def create(
        self,
        preference_data: UserPreferenceCreate
    ) -> UserPreference:
        """
        Create new user preferences.
        
        Args:
            preference_data: Preference creation data
            
        Returns:
            Created preference entity
        """
        preference = UserPreference(**preference_data.model_dump())
        self.db.add(preference)
        await self.db.commit()
        await self.db.refresh(preference)
        logger.debug(f"Created preferences for user: {preference.user_id}")
        return preference
    
    async def get_by_id(self, preference_id: str) -> Optional[UserPreference]:
        """
        Get user preference by ID.
        
        Args:
            preference_id: Preference UUID as string
            
        Returns:
            Preference if found, None otherwise
        """
        try:
            uuid_obj = UUID(preference_id)
            preference = await self.db.get(UserPreference, uuid_obj)
            return preference
        except ValueError:
            logger.warning(f"Invalid UUID format: {preference_id}")
            return None
    
    async def get_by_user_id(self, user_id: str) -> Optional[UserPreference]:
        """
        Get user preference by user ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            Preference if found, None otherwise
        """
        statement = select(UserPreference).where(
            UserPreference.user_id == user_id
        )
        result = await self.db.execute(statement)
        preference = result.scalars().first()
        return preference
    
    async def update(
        self,
        user_id: str,
        preference_data: UserPreferenceUpdate
    ) -> Optional[UserPreference]:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            preference_data: Update data
            
        Returns:
            Updated preference if found, None otherwise
        """
        preference = await self.get_by_user_id(user_id)
        if not preference:
            return None
        
        # Update fields
        update_dict = preference_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(preference, key, value)
        
        preference.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        
        self.db.add(preference)
        await self.db.commit()
        await self.db.refresh(preference)
        
        logger.debug(f"Updated preferences for user: {user_id}")
        return preference
    
    async def delete(self, user_id: str) -> bool:
        """
        Delete user preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted, False if not found
        """
        preference = await self.get_by_user_id(user_id)
        if not preference:
            return False
        
        await self.db.delete(preference)
        await self.db.commit()
        
        logger.debug(f"Deleted preferences for user: {user_id}")
        return True
    
    async def get_or_create(
        self,
        user_id: str
    ) -> UserPreference:
        """
        Get existing preferences or create with defaults.
        
        Args:
            user_id: User identifier
            
        Returns:
            User preference (existing or newly created)
        """
        preference = await self.get_by_user_id(user_id)
        
        if preference:
            return preference
        
        # Create with defaults
        new_preference = UserPreferenceCreate(user_id=user_id)
        return await self.create(new_preference)


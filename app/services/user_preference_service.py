"""
User Preference Service - Business Logic for User Preferences

Handles user preference management including retrieval, creation, and updates.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user_preference_repository import UserPreferenceRepository
from app.models.user_preference_model import UserPreference
from app.schemas.user_preference_schema import (
    UserPreferenceCreate,
    UserPreferenceUpdate
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserPreferenceService:
    """Service class for user preference business logic."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize service with database session.
        
        Args:
            db: Async database session
        """
        self.db = db
        self.preference_repo = UserPreferenceRepository(db)
    
    async def get_or_create_preferences(
        self,
        user_id: str
    ) -> UserPreference:
        """
        Get user preferences or create with defaults if not exists.
        
        Args:
            user_id: User identifier
            
        Returns:
            User preference entity
        """
        logger.debug(f"Getting preferences for user: {user_id}")
        return await self.preference_repo.get_or_create(user_id)
    
    async def get_preferences(
        self,
        user_id: str
    ) -> Optional[UserPreference]:
        """
        Get user preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            User preference if exists, None otherwise
        """
        return await self.preference_repo.get_by_user_id(user_id)
    
    async def update_preferences(
        self,
        user_id: str,
        preferences: UserPreferenceUpdate
    ) -> Optional[UserPreference]:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            preferences: Update data
            
        Returns:
            Updated preferences if user exists, None otherwise
        """
        logger.info(f"Updating preferences for user: {user_id}")
        
        updated = await self.preference_repo.update(user_id, preferences)
        
        if updated:
            logger.info(f"Successfully updated preferences for user: {user_id}")
        else:
            logger.warning(f"User not found: {user_id}")
        
        return updated
    
    async def create_preferences(
        self,
        preferences: UserPreferenceCreate
    ) -> UserPreference:
        """
        Create new user preferences.
        
        Args:
            preferences: Preference creation data
            
        Returns:
            Created preference entity
        """
        logger.info(f"Creating preferences for user: {preferences.user_id}")
        return await self.preference_repo.create(preferences)
    
    async def delete_preferences(
        self,
        user_id: str
    ) -> bool:
        """
        Delete user preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting preferences for user: {user_id}")
        return await self.preference_repo.delete(user_id)


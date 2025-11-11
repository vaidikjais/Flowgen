"""
User Preference Controller - API Endpoints for User Preferences

Handles user preference retrieval and updates.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.user_preference_service import UserPreferenceService
from app.schemas.user_preference_schema import (
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceOut
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/preferences", tags=["User Preferences"])


def get_preference_service(db: AsyncSession = Depends(get_session)) -> UserPreferenceService:
    """Dependency injection for user preference service."""
    return UserPreferenceService(db)


@router.get("", response_model=UserPreferenceOut, tags=["User Preferences"])
async def get_preferences(
    user_id: str = Query(..., description="User identifier"),
    service: UserPreferenceService = Depends(get_preference_service)
):
    """
    Get user preferences.
    
    Returns existing preferences or creates defaults if not found.
    """
    logger.debug(f"Get preferences for user: {user_id}")
    
    try:
        preferences = await service.get_or_create_preferences(user_id)
        return UserPreferenceOut.model_validate(preferences)
        
    except Exception as e:
        logger.error(f"Failed to get preferences: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve preferences: {str(e)}"
        )


@router.put("", response_model=UserPreferenceOut, tags=["User Preferences"])
async def update_preferences(
    user_id: str = Query(..., description="User identifier"),
    preferences: UserPreferenceUpdate = ...,
    service: UserPreferenceService = Depends(get_preference_service)
):
    """
    Update user preferences.
    
    Creates preferences if they don't exist, updates if they do.
    """
    logger.info(f"Update preferences for user: {user_id}")
    
    try:
        # Try to update existing preferences
        updated = await service.update_preferences(user_id, preferences)
        
        if not updated:
            # Create new preferences if they don't exist
            create_data = UserPreferenceCreate(
                user_id=user_id,
                **(preferences.model_dump(exclude_unset=True))
            )
            updated = await service.create_preferences(create_data)
        
        return UserPreferenceOut.model_validate(updated)
        
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.delete("", tags=["User Preferences"])
async def delete_preferences(
    user_id: str = Query(..., description="User identifier"),
    service: UserPreferenceService = Depends(get_preference_service)
):
    """
    Delete user preferences.
    
    Returns a success message if deleted, 404 if not found.
    """
    logger.info(f"Delete preferences for user: {user_id}")
    
    try:
        deleted = await service.delete_preferences(user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Preferences not found for user: {user_id}"
            )
        
        return {"message": "Preferences deleted successfully", "user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete preferences: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete preferences: {str(e)}"
        )


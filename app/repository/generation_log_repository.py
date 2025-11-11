"""
Generation Log Repository - Data Access Layer for Generation Logs

Handles all database operations for generation log entities.
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.models.generation_log_model import GenerationLog

logger = logging.getLogger(__name__)


class GenerationLogRepository:
    """Repository class for generation log database operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def create(
        self,
        prompt: str,
        prompt_hash: str,
        success: bool,
        tokens_used: Optional[int] = None,
        model_used: Optional[str] = None,
        latency_ms: Optional[int] = None,
        total_time_ms: Optional[int] = None,
        error_message: Optional[str] = None,
        error_type: Optional[str] = None,
        was_cached: bool = False,
        user_id: Optional[str] = None,
        diagram_id: Optional[UUID] = None
    ) -> GenerationLog:
        """
        Create a new generation log entry.
        
        Args:
            prompt: User prompt
            prompt_hash: Hash of the prompt
            success: Whether generation was successful
            tokens_used: Number of tokens consumed
            model_used: LLM model used
            latency_ms: LLM call latency in milliseconds
            total_time_ms: Total time including rendering
            error_message: Error message if failed
            error_type: Type of error
            was_cached: Whether result was from cache
            user_id: User identifier
            diagram_id: Related diagram ID
            
        Returns:
            Created log entry
        """
        log = GenerationLog(
            prompt=prompt,
            prompt_hash=prompt_hash,
            success=success,
            tokens_used=tokens_used,
            model_used=model_used,
            latency_ms=latency_ms,
            total_time_ms=total_time_ms,
            error_message=error_message,
            error_type=error_type,
            was_cached=was_cached,
            user_id=user_id,
            diagram_id=diagram_id
        )
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        logger.debug(f"Created generation log: {log.id}")
        return log
    
    async def get_by_id(self, log_id: str) -> Optional[GenerationLog]:
        """
        Get generation log by ID.
        
        Args:
            log_id: Log UUID as string
            
        Returns:
            Log if found, None otherwise
        """
        try:
            uuid_obj = UUID(log_id)
            log = await self.db.get(GenerationLog, uuid_obj)
            return log
        except ValueError:
            logger.warning(f"Invalid UUID format: {log_id}")
            return None
    
    async def list_recent(
        self,
        limit: int = 100,
        user_id: Optional[str] = None,
        success_only: bool = False
    ) -> List[GenerationLog]:
        """
        List recent generation logs.
        
        Args:
            limit: Maximum number of logs to return
            user_id: Optional user ID filter
            success_only: If True, only return successful generations
            
        Returns:
            List of generation logs
        """
        statement = select(GenerationLog)
        
        if user_id:
            statement = statement.where(GenerationLog.user_id == user_id)
        
        if success_only:
            statement = statement.where(GenerationLog.success == True)
        
        statement = (
            statement
            .order_by(GenerationLog.created_at.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(statement)
        logs = result.scalars().all()
        return list(logs)
    
    async def get_usage_stats(
        self,
        days: int = 7,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics for analytics.
        
        Args:
            days: Number of days to analyze
            user_id: Optional user ID filter
            
        Returns:
            Dictionary with usage statistics
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_date = cutoff_date.replace(tzinfo=None)
        
        # Build base query
        statement = select(
            func.count(GenerationLog.id).label("total_requests"),
            func.sum(GenerationLog.tokens_used).label("total_tokens"),
            func.avg(GenerationLog.latency_ms).label("avg_latency_ms"),
            func.sum(
                func.cast(GenerationLog.success, func.INTEGER())
            ).label("successful_requests"),
            func.sum(
                func.cast(GenerationLog.was_cached, func.INTEGER())
            ).label("cached_requests"),
        ).where(GenerationLog.created_at >= cutoff_date)
        
        if user_id:
            statement = statement.where(GenerationLog.user_id == user_id)
        
        result = await self.db.execute(statement)
        row = result.first()
        
        if not row:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "avg_latency_ms": 0,
                "successful_requests": 0,
                "cached_requests": 0,
                "success_rate": 0.0,
                "cache_hit_rate": 0.0,
                "period_days": days
            }
        
        total_requests = row.total_requests or 0
        successful_requests = row.successful_requests or 0
        cached_requests = row.cached_requests or 0
        
        return {
            "total_requests": total_requests,
            "total_tokens": row.total_tokens or 0,
            "avg_latency_ms": round(row.avg_latency_ms or 0, 2),
            "successful_requests": successful_requests,
            "cached_requests": cached_requests,
            "success_rate": (
                round(successful_requests / total_requests * 100, 2)
                if total_requests > 0 else 0.0
            ),
            "cache_hit_rate": (
                round(cached_requests / total_requests * 100, 2)
                if total_requests > 0 else 0.0
            ),
            "period_days": days
        }
    
    async def delete_old(self, days: int = 90) -> int:
        """
        Delete logs older than specified days.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_date = cutoff_date.replace(tzinfo=None)
        
        statement = select(GenerationLog).where(
            GenerationLog.created_at < cutoff_date
        )
        result = await self.db.execute(statement)
        old_logs = result.scalars().all()
        
        count = len(old_logs)
        
        for log in old_logs:
            await self.db.delete(log)
        
        await self.db.commit()
        
        logger.info(f"Deleted {count} old generation logs (older than {days} days)")
        return count


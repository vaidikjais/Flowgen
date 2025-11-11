"""
Cleanup Old Diagrams Script

Removes old diagrams and generation logs from the database
based on retention policies.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.repository.diagram_repository import DiagramRepository
from app.repository.generation_log_repository import GenerationLogRepository


async def cleanup_old_diagrams(
    db: AsyncSession,
    days: int = None
) -> int:
    """
    Delete diagrams older than specified days.
    
    Args:
        db: Database session
        days: Number of days to retain (uses CACHE_RETENTION_DAYS from config if not specified)
        
    Returns:
        Number of diagrams deleted
    """
    if days is None:
        days = settings.CACHE_RETENTION_DAYS
    
    diagram_repo = DiagramRepository(db)
    
    print(f"Deleting diagrams older than {days} days...")
    count = await diagram_repo.delete_old(days=days)
    await db.commit()
    
    print(f"  ✓ Deleted {count} old diagrams")
    return count


async def cleanup_old_logs(
    db: AsyncSession,
    days: int = 90
) -> int:
    """
    Delete generation logs older than specified days.
    
    Args:
        db: Database session
        days: Number of days to retain logs
        
    Returns:
        Number of logs deleted
    """
    log_repo = GenerationLogRepository(db)
    
    print(f"Deleting generation logs older than {days} days...")
    count = await log_repo.delete_old(days=days)
    await db.commit()
    
    print(f"  ✓ Deleted {count} old generation logs")
    return count


async def main():
    """Main cleanup function."""
    print("=" * 60)
    print("DiagramGPT - Database Cleanup Script")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create session and cleanup data
    async with AsyncSessionLocal() as session:
        try:
            # Cleanup old diagrams
            diagram_count = await cleanup_old_diagrams(session)
            
            # Cleanup old logs (keep for 90 days)
            log_count = await cleanup_old_logs(session, days=90)
            
            print()
            print("=" * 60)
            print("✓ Database cleanup completed successfully!")
            print(f"  - Diagrams deleted: {diagram_count}")
            print(f"  - Logs deleted: {log_count}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error during cleanup: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())


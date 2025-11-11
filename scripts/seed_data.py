"""
Seed Data Script

Populates the database with sample diagrams and user preferences
for testing and demonstration purposes.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, create_db_and_tables
from app.repository.diagram_repository import DiagramRepository
from app.repository.user_preference_repository import UserPreferenceRepository
from app.schemas.diagram_schema import DiagramCreate
from app.schemas.user_preference_schema import UserPreferenceCreate
from app.utils.hash_utils import hash_prompt


SAMPLE_DIAGRAMS = [
    {
        "prompt": "Create a simple login flowchart",
        "dot_code": """digraph login {
    rankdir=TB;
    node [shape=box, style=rounded];
    
    start [label="Start", shape=ellipse];
    input [label="Enter Credentials"];
    validate [label="Validate"];
    success [label="Login Success", shape=ellipse, style=filled, fillcolor=lightgreen];
    error [label="Login Failed", shape=ellipse, style=filled, fillcolor=lightcoral];
    
    start -> input;
    input -> validate;
    validate -> success [label="Valid"];
    validate -> error [label="Invalid"];
}""",
        "format": "svg",
        "layout": "dot",
    },
    {
        "prompt": "Draw a network topology with 4 nodes",
        "dot_code": """graph network {
    node [shape=circle];
    
    A [label="Node A"];
    B [label="Node B"];
    C [label="Node C"];
    D [label="Node D"];
    
    A -- B;
    B -- C;
    C -- D;
    D -- A;
    A -- C;
}""",
        "format": "svg",
        "layout": "neato",
    },
    {
        "prompt": "Create a simple class diagram",
        "dot_code": """digraph classes {
    rankdir=TB;
    node [shape=record];
    
    User [label="{User|+ id: UUID\\l+ name: String\\l|+ login()\\l+ logout()\\l}"];
    Post [label="{Post|+ id: UUID\\l+ title: String\\l|+ publish()\\l+ delete()\\l}"];
    Comment [label="{Comment|+ id: UUID\\l+ text: String\\l|+ create()\\l}"];
    
    User -> Post [label="creates", arrowhead=vee];
    Post -> Comment [label="has many", arrowhead=crow];
}""",
        "format": "svg",
        "layout": "dot",
    },
]

SAMPLE_USERS = [
    {
        "user_id": "test_user_1",
        "default_format": "svg",
        "default_layout": "dot",
        "theme": "light",
    },
    {
        "user_id": "test_user_2",
        "default_format": "png",
        "default_layout": "neato",
        "theme": "dark",
    },
]


async def seed_diagrams(db: AsyncSession):
    """Seed sample diagrams."""
    diagram_repo = DiagramRepository(db)
    
    print("Seeding diagrams...")
    for idx, diagram_data in enumerate(SAMPLE_DIAGRAMS, 1):
        prompt_hash = hash_prompt(
            diagram_data["prompt"],
            diagram_data["format"],
            diagram_data["layout"]
        )
        
        diagram = DiagramCreate(
            prompt=diagram_data["prompt"],
            prompt_hash=prompt_hash,
            dot_code=diagram_data["dot_code"],
            format=diagram_data["format"],
            layout=diagram_data["layout"],
            user_id="test_user_1",
            token_count=150,
            generation_time_ms=500
        )
        
        created = await diagram_repo.create(diagram)
        print(f"  ✓ Created diagram {idx}: {created.id} - {diagram_data['prompt'][:50]}...")
    
    await db.commit()
    print(f"✓ Seeded {len(SAMPLE_DIAGRAMS)} diagrams")


async def seed_user_preferences(db: AsyncSession):
    """Seed sample user preferences."""
    preference_repo = UserPreferenceRepository(db)
    
    print("Seeding user preferences...")
    for idx, user_data in enumerate(SAMPLE_USERS, 1):
        preference = UserPreferenceCreate(**user_data)
        
        created = await preference_repo.create(preference)
        print(f"  ✓ Created preferences for user: {created.user_id}")
    
    await db.commit()
    print(f"✓ Seeded {len(SAMPLE_USERS)} user preferences")


async def main():
    """Main seeding function."""
    print("=" * 60)
    print("DiagramGPT - Database Seeding Script")
    print("=" * 60)
    
    # Ensure tables exist
    print("\nEnsuring database tables exist...")
    await create_db_and_tables()
    
    # Create session and seed data
    async with AsyncSessionLocal() as session:
        try:
            await seed_diagrams(session)
            await seed_user_preferences(session)
            
            print("\n" + "=" * 60)
            print("✓ Database seeding completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error seeding database: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())


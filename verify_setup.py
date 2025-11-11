#!/usr/bin/env python3
"""
Setup Verification Script

Validates that the DiagramGPT refactoring is complete and all components
are properly structured.
"""
import sys
from pathlib import Path

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - File not found: {filepath}")
        return False

def check_file_not_exists(filepath: str, description: str) -> bool:
    """Check that a file does NOT exist (has been removed)."""
    if not Path(filepath).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - File should be removed: {filepath}")
        return False

def check_directory_exists(dirpath: str, description: str) -> bool:
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - Directory not found: {dirpath}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("DiagramGPT Clean Architecture Verification")
    print("=" * 60)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # Check old files are removed
    print("Checking old files are removed...")
    checks_total += 4
    checks_passed += check_file_not_exists("app/llm_client.py", "Old llm_client.py removed")
    checks_passed += check_file_not_exists("app/diagram_renderer.py", "Old diagram_renderer.py removed")
    checks_passed += check_file_not_exists("app/schemas.py", "Old schemas.py removed")
    checks_passed += check_file_not_exists("tests/test_render.py", "Old test_render.py removed")
    print()
    
    # Check new directory structure
    print("Checking new directory structure...")
    checks_total += 7
    checks_passed += check_directory_exists("app/controller", "Controller layer")
    checks_passed += check_directory_exists("app/services", "Service layer")
    checks_passed += check_directory_exists("app/repository", "Repository layer")
    checks_passed += check_directory_exists("app/models", "Models layer")
    checks_passed += check_directory_exists("app/schemas", "Schemas layer")
    checks_passed += check_directory_exists("app/core", "Core modules")
    checks_passed += check_directory_exists("app/middleware", "Middleware")
    print()
    
    # Check controller files
    print("Checking controller files...")
    checks_total += 3
    checks_passed += check_file_exists("app/controller/diagram_controller.py", "Diagram controller")
    checks_passed += check_file_exists("app/controller/user_preference_controller.py", "User preference controller")
    checks_passed += check_file_exists("app/controller/health_controller.py", "Health controller")
    print()
    
    # Check service files
    print("Checking service files...")
    checks_total += 5
    checks_passed += check_file_exists("app/services/diagram_service.py", "Diagram service")
    checks_passed += check_file_exists("app/services/llm_service.py", "LLM service")
    checks_passed += check_file_exists("app/services/render_service.py", "Render service")
    checks_passed += check_file_exists("app/services/cache_service.py", "Cache service")
    checks_passed += check_file_exists("app/services/user_preference_service.py", "User preference service")
    print()
    
    # Check repository files
    print("Checking repository files...")
    checks_total += 3
    checks_passed += check_file_exists("app/repository/diagram_repository.py", "Diagram repository")
    checks_passed += check_file_exists("app/repository/user_preference_repository.py", "User preference repository")
    checks_passed += check_file_exists("app/repository/generation_log_repository.py", "Generation log repository")
    print()
    
    # Check model files
    print("Checking model files...")
    checks_total += 3
    checks_passed += check_file_exists("app/models/diagram_model.py", "Diagram model")
    checks_passed += check_file_exists("app/models/user_preference_model.py", "User preference model")
    checks_passed += check_file_exists("app/models/generation_log_model.py", "Generation log model")
    print()
    
    # Check schema files
    print("Checking schema files...")
    checks_total += 3
    checks_passed += check_file_exists("app/schemas/diagram_schema.py", "Diagram schemas")
    checks_passed += check_file_exists("app/schemas/user_preference_schema.py", "User preference schemas")
    checks_passed += check_file_exists("app/schemas/common_schema.py", "Common schemas")
    print()
    
    # Check core files
    print("Checking core files...")
    checks_total += 3
    checks_passed += check_file_exists("app/core/config.py", "Configuration")
    checks_passed += check_file_exists("app/core/database.py", "Database setup")
    checks_passed += check_file_exists("app/core/exceptions.py", "Custom exceptions")
    print()
    
    # Check utilities
    print("Checking utilities...")
    checks_total += 2
    checks_passed += check_file_exists("app/utils/logger.py", "Logger utility")
    checks_passed += check_file_exists("app/utils/hash_utils.py", "Hash utility")
    print()
    
    # Check middleware
    print("Checking middleware...")
    checks_total += 2
    checks_passed += check_file_exists("app/middleware/request_id.py", "Request ID middleware")
    checks_passed += check_file_exists("app/middleware/error_handler.py", "Error handler middleware")
    print()
    
    # Check test structure
    print("Checking test structure...")
    checks_total += 5
    checks_passed += check_directory_exists("tests/unit", "Unit tests directory")
    checks_passed += check_directory_exists("tests/integration", "Integration tests directory")
    checks_passed += check_file_exists("tests/conftest.py", "Test configuration")
    checks_passed += check_file_exists("tests/unit/test_hash_utils.py", "Hash utils tests")
    checks_passed += check_file_exists("tests/unit/test_render_service.py", "Render service tests")
    print()
    
    # Check scripts
    print("Checking scripts...")
    checks_total += 2
    checks_passed += check_file_exists("scripts/seed_data.py", "Seed data script")
    checks_passed += check_file_exists("scripts/cleanup_old_diagrams.py", "Cleanup script")
    print()
    
    # Check Alembic
    print("Checking Alembic setup...")
    checks_total += 2
    checks_passed += check_file_exists("alembic.ini", "Alembic configuration")
    checks_passed += check_file_exists("alembic/env.py", "Alembic environment")
    print()
    
    # Check documentation
    print("Checking documentation...")
    checks_total += 3
    checks_passed += check_file_exists("QUICK_START.md", "Quick start guide")
    checks_passed += check_file_exists("REFACTORING_SUMMARY.md", "Refactoring summary")
    checks_passed += check_file_exists("docs/architecture/clean-architecture.md", "Architecture documentation")
    print()
    
    # Final summary
    print("=" * 60)
    print(f"Verification Results: {checks_passed}/{checks_total} checks passed")
    print("=" * 60)
    
    if checks_passed == checks_total:
        print("✅ All checks passed! The refactoring is complete.")
        print()
        print("Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Set up database: createdb diagramgpt && alembic upgrade head")
        print("  3. Run application: uvicorn app.main:app --reload")
        return 0
    else:
        print(f"❌ {checks_total - checks_passed} checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""
Run all migrations on startup
This ensures the database is always up to date with the code
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_all_migrations():
    """Run all migration scripts in the migrations folder."""
    migrations_dir = Path(__file__).parent / "migrations"
    
    if not migrations_dir.exists():
        logger.warning(f"Migrations directory not found: {migrations_dir}")
        return
    
    # Get all Python migration files
    migration_files = sorted(migrations_dir.glob("*.py"))
    
    if not migration_files:
        logger.info("No migration files found")
        return
    
    logger.info(f"Found {len(migration_files)} migration files")
    
    for migration_file in migration_files:
        if migration_file.name == "__init__.py":
            continue
            
        logger.info(f"Running migration: {migration_file.name}")
        
        # Import and run the migration
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                migration_file.stem, 
                migration_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Call the run_migration function if it exists
            if hasattr(module, 'run_migration'):
                success = module.run_migration()
                if success:
                    logger.info(f"✓ Migration {migration_file.name} completed successfully")
                else:
                    logger.error(f"✗ Migration {migration_file.name} failed")
            else:
                logger.warning(f"Migration {migration_file.name} has no run_migration function")
                
        except Exception as e:
            logger.error(f"Failed to run migration {migration_file.name}: {str(e)}")
            # Continue with other migrations even if one fails

if __name__ == "__main__":
    logger.info("Starting database migrations...")
    run_all_migrations()
    logger.info("Migration runner completed")

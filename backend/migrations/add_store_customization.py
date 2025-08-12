#!/usr/bin/env python3
"""
Migration script to add store customization fields to users table
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """Add store_name, store_slug, and banner_url columns to users table."""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logger.error("DATABASE_URL not found in environment variables")
        return False
    
    engine = create_engine(DATABASE_URL)
    is_sqlite = 'sqlite' in DATABASE_URL.lower()
    
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            existing_columns = []
            
            if is_sqlite:
                # SQLite approach
                result = conn.execute(text("PRAGMA table_info(users)"))
                existing_columns = [row[1] for row in result]  # column name is at index 1
            else:
                # PostgreSQL approach
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' 
                    AND column_name IN ('store_name', 'store_slug', 'banner_url')
                """))
                existing_columns = [row[0] for row in result]
            
            # Add store_name column if it doesn't exist
            if 'store_name' not in existing_columns:
                logger.info("Adding store_name column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN store_name VARCHAR(255)
                """))
                conn.commit()
                logger.info("✓ store_name column added")
            else:
                logger.info("store_name column already exists")
            
            # Add store_slug column if it doesn't exist
            if 'store_slug' not in existing_columns:
                logger.info("Adding store_slug column...")
                
                if is_sqlite:
                    # SQLite doesn't support adding UNIQUE in ALTER TABLE
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN store_slug VARCHAR(100)
                    """))
                    conn.commit()
                    
                    # Create unique index instead
                    conn.execute(text("""
                        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_store_slug_unique 
                        ON users(store_slug)
                    """))
                    conn.commit()
                else:
                    # PostgreSQL supports UNIQUE in ALTER TABLE
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN store_slug VARCHAR(100) UNIQUE
                    """))
                    conn.commit()
                    
                    # Create index for faster lookups
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_users_store_slug 
                        ON users(store_slug)
                    """))
                    conn.commit()
                
                logger.info("✓ store_slug column added with unique constraint and index")
            else:
                logger.info("store_slug column already exists")
            
            # Add banner_url column if it doesn't exist
            if 'banner_url' not in existing_columns:
                logger.info("Adding banner_url column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN banner_url TEXT
                """))
                conn.commit()
                logger.info("✓ banner_url column added")
            else:
                logger.info("banner_url column already exists")
            
            logger.info("Migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

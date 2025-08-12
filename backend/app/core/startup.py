"""
Startup tasks for the application
"""
import os
import logging
from sqlalchemy import create_engine, text
from typing import Optional

logger = logging.getLogger(__name__)

def fix_broken_image_urls(database_url: Optional[str] = None):
    """
    Fix products with local image URLs that won't work in production.
    This runs on startup to ensure all products have valid image URLs.
    """
    if not database_url:
        database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.warning("No DATABASE_URL found, skipping image URL fix")
        return
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Count products with local image URLs
            result = conn.execute(text('''
                SELECT COUNT(*) FROM products 
                WHERE image_url_1 LIKE '/uploads/%'
                   OR image_url_1 LIKE 'uploads/%'
                   OR image_url_2 LIKE '/uploads/%'
                   OR image_url_2 LIKE 'uploads/%'
                   OR image_url_3 LIKE '/uploads/%'
                   OR image_url_3 LIKE 'uploads/%'
                   OR image_url_4 LIKE '/uploads/%'
                   OR image_url_4 LIKE 'uploads/%'
                   OR image_url_5 LIKE '/uploads/%'
                   OR image_url_5 LIKE 'uploads/%'
            '''))
            
            count = result.scalar()
            
            if count == 0:
                logger.info("No products with local image URLs found")
                return
            
            logger.warning(f"Found {count} products with local image URLs that need fixing")
            
            # In production, replace local URLs with a placeholder or NULL
            # This prevents 404 errors for images that don't exist
            if os.getenv("RENDER") or os.getenv("ENVIRONMENT") == "production":
                logger.info("Running in production - clearing broken local image URLs")
                
                # Update all local image URLs to NULL
                for i in range(1, 6):
                    update_sql = text(f'''
                        UPDATE products 
                        SET image_url_{i} = NULL
                        WHERE image_url_{i} LIKE '/uploads/%'
                           OR image_url_{i} LIKE 'uploads/%'
                    ''')
                    
                    result = conn.execute(update_sql)
                    if result.rowcount > 0:
                        logger.info(f"Cleared {result.rowcount} broken URLs from image_url_{i}")
                
                conn.commit()
                logger.info("Successfully cleaned up broken image URLs")
            else:
                logger.info("Running in development - keeping local image URLs")
                
    except Exception as e:
        logger.error(f"Error fixing broken image URLs: {e}")
        # Don't fail startup if this fails
        pass

def ensure_uploads_directory():
    """
    Ensure the uploads directory exists for local file storage.
    """
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        logger.info(f"Created uploads directory: {uploads_dir}")
        
        # Create a placeholder file
        gitkeep_path = os.path.join(uploads_dir, ".gitkeep")
        with open(gitkeep_path, "w") as f:
            f.write("# This directory stores uploaded images locally\n")
        logger.info(f"Created .gitkeep file in uploads directory")

def run_startup_tasks():
    """
    Run all startup tasks.
    """
    logger.info("Running startup tasks...")
    
    # Ensure uploads directory exists
    ensure_uploads_directory()
    
    # Fix broken image URLs in production
    fix_broken_image_urls()
    
    logger.info("Startup tasks completed")

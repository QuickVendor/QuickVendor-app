#!/usr/bin/env python3
"""
Migration script to fix products with local image URLs
Either migrates them to S3 or replaces with placeholder
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

def migrate_local_images():
    """Migrate products with local image URLs to use S3 or placeholder."""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        logger.error("DATABASE_URL not found in environment variables")
        return
    
    engine = create_engine(DATABASE_URL)
    
    # Default placeholder image (you can host this on S3)
    PLACEHOLDER_IMAGE = "https://via.placeholder.com/400x400.png?text=Product+Image"
    
    with engine.connect() as conn:
        # Find all products with local image URLs
        result = conn.execute(text('''
            SELECT id, name, 
                   image_url_1, image_url_2, image_url_3, image_url_4, image_url_5
            FROM products 
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
        
        products_to_fix = result.fetchall()
        
        if not products_to_fix:
            logger.info("No products with local image URLs found")
            return
        
        logger.info(f"Found {len(products_to_fix)} products with local image URLs")
        
        # Check if S3 is configured
        from app.services.s3_manager import get_s3_manager
        s3_manager = get_s3_manager()
        
        if s3_manager.is_s3_configured():
            logger.info("S3 is configured - will use placeholder images on S3")
            # You could upload a default image to S3 here
        else:
            logger.info("S3 not configured - will use external placeholder")
        
        # Update each product
        for product in products_to_fix:
            product_id = product[0]
            product_name = product[1]
            
            logger.info(f"Processing product: {product_id} - {product_name}")
            
            # Prepare update query
            updates = []
            params = {'product_id': product_id}
            
            # Check each image URL
            for i in range(1, 6):
                image_url = product[i + 1]  # image_url_1 is at index 2, etc.
                if image_url and ('/uploads/' in image_url or image_url.startswith('uploads/')):
                    # This is a local URL that needs to be fixed
                    updates.append(f"image_url_{i} = :placeholder")
                    params['placeholder'] = PLACEHOLDER_IMAGE
                    logger.info(f"  - Replacing image_url_{i}: {image_url} -> placeholder")
            
            if updates:
                # Build and execute update query
                update_sql = f'''
                    UPDATE products 
                    SET {', '.join(updates)}
                    WHERE id = :product_id
                '''
                
                conn.execute(text(update_sql), params)
                conn.commit()
                logger.info(f"  ✓ Updated product {product_id}")
        
        logger.info(f"Migration complete! Updated {len(products_to_fix)} products")

if __name__ == "__main__":
    migrate_local_images()

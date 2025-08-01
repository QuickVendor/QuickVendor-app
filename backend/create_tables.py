#!/usr/bin/env python3
"""
Database table creation script for PostgreSQL
Run this script to create all database tables
"""

from app.core.database import engine, Base
from app.models.user import User
from app.models.product import Product

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    
    try:
        # Import all models to ensure they're registered with Base
        from app.models import user, product
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()

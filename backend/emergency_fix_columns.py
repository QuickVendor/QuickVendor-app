#!/usr/bin/env python3
"""
EMERGENCY FIX: Add missing columns to production database
Run this on Render shell to fix the database immediately
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    exit(1)

print(f"Connecting to database...")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Checking and adding missing columns...")
    
    try:
        # Try to add store_name
        print("Adding store_name column...")
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS store_name VARCHAR(255)"))
        conn.commit()
        print("✓ store_name column added or already exists")
    except Exception as e:
        print(f"Note: {e}")
    
    try:
        # Try to add store_slug
        print("Adding store_slug column...")
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS store_slug VARCHAR(100)"))
        conn.commit()
        print("✓ store_slug column added or already exists")
    except Exception as e:
        print(f"Note: {e}")
    
    try:
        # Try to add banner_url
        print("Adding banner_url column...")
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS banner_url TEXT"))
        conn.commit()
        print("✓ banner_url column added or already exists")
    except Exception as e:
        print(f"Note: {e}")
    
    try:
        # Add unique constraint to store_slug if not exists
        print("Adding unique constraint to store_slug...")
        conn.execute(text("""
            ALTER TABLE users 
            ADD CONSTRAINT users_store_slug_key UNIQUE (store_slug)
        """))
        conn.commit()
        print("✓ Unique constraint added to store_slug")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("✓ Unique constraint already exists")
        else:
            print(f"Note: {e}")
    
    try:
        # Create index for store_slug
        print("Creating index on store_slug...")
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_store_slug ON users(store_slug)"))
        conn.commit()
        print("✓ Index created on store_slug")
    except Exception as e:
        print(f"Note: {e}")
    
    # Verify columns exist
    print("\nVerifying columns...")
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' 
        AND column_name IN ('store_name', 'store_slug', 'banner_url')
    """))
    
    columns = [row[0] for row in result]
    print(f"Found columns: {columns}")
    
    if len(columns) == 3:
        print("\n✅ SUCCESS! All columns are now present in the database.")
    else:
        missing = set(['store_name', 'store_slug', 'banner_url']) - set(columns)
        print(f"\n⚠️ WARNING: Missing columns: {missing}")

print("\nDone! You can now try logging in again.")

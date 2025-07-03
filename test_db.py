#!/usr/bin/env python3
from database import engine
import os

print("Testing database connection...")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")

try:
    with engine.connect() as conn:
        from sqlalchemy import text
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Database connection failed: {e}") 
import asyncio
import sys
import os

# Add the current directory to sys.path to allow importing 'app'
sys.path.append(os.getcwd())

from app.database import engine, Base
from app.models import user, account, stage
from sqlalchemy import text

async def create_tables():
    print("Starting table creation...")
    try:
        async with engine.begin() as conn:
            # This will create all tables defined in models
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")
        
        # Verify sync
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result]
            print(f"Verified tables in DB: {tables}")
            
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_tables())

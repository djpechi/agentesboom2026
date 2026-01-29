import asyncio
import sys
from sqlalchemy import select

# Add current directory to path so we can import app
import os
sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app.models.user import User
from app.utils.security import hash_password

async def create_test_user():
    email = "lalo@test.com"
    password = "password123"
    full_name = "Lalo Solis"
    
    async with AsyncSessionLocal() as db:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ User already exists: {email}")
            print(f"📧 Email: {email}")
            print(f"🔑 Password: {password}")
            return

        # Create new user
        hashed = hash_password(password)
        new_user = User(
            email=email,
            hashed_password=hashed,
            full_name=full_name
        )
        
        db.add(new_user)
        try:
            await db.commit()
            print(f"🎉 Created test user successfully!")
            print(f"👤 Name: {full_name}")
            print(f"📧 Email: {email}")
            print(f"🔑 Password: {password}")
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(create_test_user())

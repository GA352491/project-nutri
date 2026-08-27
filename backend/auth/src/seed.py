import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from auth_service.models.user import User, Base
from auth_service.services.auth_service import hash_password
from auth_service.config import settings

async def seed_users():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        users = [
            User(
                email="admin@nutriplan.local",
                hashed_password=hash_password("Admin@123"),
                full_name="System Administrator",
                role="admin",
                is_active=True,
                is_verified=True
            ),
            User(
                email="expert@nutriplan.local",
                hashed_password=hash_password("Expert@123"),
                full_name="Dr. Sarah Jenkins",
                role="nutritionist",
                is_active=True,
                is_verified=True
            ),
            User(
                email="patient@nutriplan.local",
                hashed_password=hash_password("Patient@123"),
                full_name="Jane Doe",
                role="patient",
                is_active=True,
                is_verified=True
            ),
            User(
                email="test@test.com",
                hashed_password=hash_password("Test@123"),
                full_name="Test User",
                role="member",
                is_active=True,
                is_verified=True
            )
        ]
        
        for u in users:
            existing = await session.execute(select(User).where(User.email == u.email))
            if not existing.scalar_one_or_none():
                session.add(u)
                print(f"Seeded user: {u.email}")
            else:
                print(f"User already exists: {u.email}")
        
        await session.commit()
    print("✅ PostgreSQL Auth DB Seeding Complete!")

if __name__ == "__main__":
    asyncio.run(seed_users())

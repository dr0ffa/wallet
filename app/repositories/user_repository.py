from models_db.models import User

from core.security import hash_password, verify_password

from sqlalchemy import select
from fastapi import HTTPException

from sqlmodel.ext.asyncio.session import AsyncSession


async def register_user(session: AsyncSession, email: str, username: str, password: str):
    result = await session.scalars(select(User).where(User.username == username))
    existing_user = result.all()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    
    new_user = User(email=email, username=username, hashed_password=hash_password(password))
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return {"message": "User created successfully", "user_id": new_user.id}

async def login_user(session: AsyncSession, email: str, username: str, password: str):
    result = await session.scalars(select(User).where(User.email == email, User.username == username))
    user = result.first()
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    return {"username": user.username, "email": user.email, "user_id": user.id, "message": "Login successful"}

async def get_user_id(session: AsyncSession, username: str):
    result = await session.scalars(select(User).where(User.username == username))
    user = result.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user_id": str(user.id)}

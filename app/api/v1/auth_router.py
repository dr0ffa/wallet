from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.auth_schemas import RegisterUserRequest

from models_db.database import get_db_context

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register")
async def register(request: RegisterUserRequest, session: AsyncSession = Depends(get_db_context)):
    

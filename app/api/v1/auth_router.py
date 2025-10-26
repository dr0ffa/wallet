from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.auth_schemas import RegisterUserRequest, LoginUserRequest

from models_db.database import get_db_context

from repositories.user_repository import register_user, login_user 

from core.create_token import create_access_token, create_refresh_token, validation_token, decode_token




auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register")
async def register(request: RegisterUserRequest, session: AsyncSession = Depends(get_db_context)):
    new_user = await register_user(session, request.email, request.username, request.password)
    return new_user


@auth_router.post("/login")
async def login(request: LoginUserRequest, response: Response, session: AsyncSession = Depends(get_db_context)):
    user = await login_user(session, request.email, request.username, request.password)

    access_token = create_access_token({"sub": request.username})
    refresh_token = create_refresh_token({"sub": request.username})

    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax")

    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/refresh")
async def refresh_token(request: Request, response: Response, session: AsyncSession = Depends(get_db_context)):
    refresh_token_cookie = request.cookies.get("refresh_token")
    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    try:
        payload = decode_token(refresh_token_cookie)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    new_access_token = create_access_token({"sub": username})

    response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=False, samesite="lax", max_age=60 * 60)

    return {"access_token": new_access_token, "message": "Access token refreshed"}
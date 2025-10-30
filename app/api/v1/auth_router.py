from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.auth_schemas import RegisterUserRequest, LoginUserRequest, ConfirmMFARequest

from models_db.database import get_db_context

from repositories.user_repository import register_user, login_user, get_user_id
from repositories.mfa_repository import create_mfa_record, update_mfa_record, check_mfa, active_mfa

from core.create_token import create_access_token, create_refresh_token, validation_token, validation_token_mfa
from core.totp import enable_mfa, check_totp, get_otp
from logging import getLogger

from datetime import timedelta

from jose import JWTError, ExpiredSignatureError

logger = getLogger(__name__)


auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register")
async def register(request: RegisterUserRequest, session: AsyncSession = Depends(get_db_context)):
    new_user = await register_user(session, request.email, request.username, request.password)
    user_id = new_user["user_id"]
    await create_mfa_record(session, user_id)

    return new_user


@auth_router.post("/login")
async def login(request: LoginUserRequest, response: Response, session: AsyncSession = Depends(get_db_context)):
    user = await login_user(session, request.email, request.username, request.password)

    user_data = await get_user_id(session, request.username)
    user_id = user_data["user_id"]

    mfa_record = await check_mfa(user_id, session)
    if  not (mfa_record.enabled):
        access_token = create_access_token({"sub": request.username})
        refresh_token = create_refresh_token({"sub": request.username})

        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax")
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax")

        return {"user": user, "access_token": access_token, "refresh_token": refresh_token}

    else:
        mfa_token = create_access_token({"sub": request.username}, expires_delta=timedelta(seconds=60))
        response.set_cookie(key="mfa_token", value=mfa_token, httponly=True, secure=False, samesite="lax")

        return {"message": "MFA is enabled. Please verify your code.", "user_id": user_id}


@auth_router.post("/refresh")
async def refresh_token(request: Request, response: Response, session: AsyncSession = Depends(get_db_context)):
    username = validation_token(request)
    new_access_token = create_access_token({"sub": username})
    response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=False, samesite="lax", max_age=60 * 60)

    return {"access_token": new_access_token, "message": "Access token refreshed"}


@auth_router.post("/enable_mfa")
async def enable_mfa_endpoint(request: Request, session: AsyncSession = Depends(get_db_context)):
    username = validation_token(request)
    #logger.debug(f"hand {username} ")
    user_data = await get_user_id(session, username)
    user_id = user_data["user_id"]

    result = await enable_mfa(user_id, username, session)
    secret = result["secret"]
    #logger.debug(f"hand2 {secret} ")
    await update_mfa_record(session, user_id, secret, enabled=False)

    return {"qr_code": result["qr_code"], "secret": secret, "message": "Scan QR and verify with code"}


@auth_router.post("/confirm_mfa") 
async def confirm_mfa(request: Request, body: ConfirmMFARequest, response: Response, session: AsyncSession = Depends(get_db_context)):
    otp = body.otp
    if not otp:
        raise HTTPException(status_code=400, detail="OTP code is required")
    
    try:
        username = validation_token_mfa(request)
        token_source = "mfa_token"
    except Exception as e:
        try:
            username = validation_token(request)
            token_source = "access_token"
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or missing token")

    user_data = await get_user_id(session, username)
    user_id = user_data["user_id"]
    mfa_record = await check_mfa(user_id, session)

    await check_totp(mfa_record, otp)
    await active_mfa(mfa_record, session)

    if token_source == "mfa_token":
        access_token = create_access_token({"sub": username})
        refresh_token = create_refresh_token({"sub": username})

        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax")
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax")

        response.delete_cookie("mfa_token")

        return {"message": "MFA successfully enabled and tokens issued"}

    return {"message": "MFA successfully verified"}

from fastapi import APIRouter, Depends, Request, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.wallet_schemas import CreateWalletRequest
from models_db.database import get_db_context
from core.create_token import validation_token
from repositories.wallet_repository import create_wallet




wallet_router = APIRouter(prefix="/wallet")

@wallet_router.post("/create")
async def create_new_wallet(request: Request, body: CreateWalletRequest, session: AsyncSession = Depends(get_db_context)):
    username = validation_token(request)
    res = await create_wallet(username, session, body.name, body.currency)

    return{"message": "Wallet created successfully", "res": res}

   




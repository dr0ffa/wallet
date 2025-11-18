from fastapi import APIRouter, Depends, Request, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.wallet_schemas import CreateWalletRequest, DeleteWallet, RefillWallet
from models_db.database import get_db_context
from core.create_token import validation_token
from repositories.wallet_repository import create_wallet, delete_wallet_db


# deposit, withdraw-вывод, transfer, refill - пополнение

wallet_router = APIRouter(prefix="/wallet")

@wallet_router.post("/create")
async def create_new_wallet(request: Request, body: CreateWalletRequest, session: AsyncSession = Depends(get_db_context)):
    username = validation_token(request)
    res = await create_wallet(username, session, body.name, body.currency, body.initial_balance)

    return{"message": "Wallet created successfully", "balance": body.initial_balance}


@wallet_router.delete("/delete")
async def delete_wallet(request: Request, body: DeleteWallet, session: AsyncSession = Depends(get_db_context)):
    username = validation_token(request)
    res = await delete_wallet_db(body.wallet_id, username, session)

    return{"massage": "Wallet deleted sucessfully", "wallet_id": body.wallet_id}


@wallet_router.post("/refill") # в роутер транкзакций
async def refill_wallet(request: Request, body: RefillWallet, session: AsyncSession = Depends(get_db_context)):
    username = validation_token(request)



   




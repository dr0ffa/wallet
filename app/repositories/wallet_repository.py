from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from models_db.models import Wallet

from repositories.user_repository import get_user_id
from repositories.tanc_repository import inital_transaction


async def create_wallet(username, session: AsyncSession, wallet_name, currency, initial_balance):
    user_data = await get_user_id(session, username)
    user_id = user_data["user_id"]

    result = await session.scalars(select(func.count(Wallet.id)).where(Wallet.user_id == user_id))
    wallet_count = result.one()

    if wallet_count >= 5:
        raise HTTPException(status_code=409, detail="You can create a maximum of 5 wallets")

    new_wallet = Wallet(user_id=user_id, name=wallet_name, balance=initial_balance, currency=currency)

    session.add(new_wallet)
    await session.commit()
    await session.refresh(new_wallet)

    if initial_balance > 0:
        await inital_transaction(new_wallet.id, initial_balance, currency, session)

    return {"name": new_wallet.name, "count": wallet_count}

async def delete_wallet_db(wallet_id, username, session: AsyncSession):
    user_data = await get_user_id(session, username)
    user_id = user_data["user_id"]

    result = await session.scalars(select(Wallet).where(Wallet.id == wallet_id, user_id == user_id))
    wallet = result.first()

    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    await session.delete(wallet)
    await session.commit()

    return {"massage": "wallet deleted", "wallet_name": wallet_id}




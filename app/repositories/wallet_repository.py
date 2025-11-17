from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from models_db.models import Wallet

from repositories.user_repository import register_user, login_user, get_user_id


async def create_wallet(username, session: AsyncSession, wallet_name, currency):
    user_data = await get_user_id(session, username)
    user_id = user_data["user_id"]

    result = await session.scalars(select(func.count(Wallet.id)).where(Wallet.user_id == user_id))
    wallet_count = result.one()

    if wallet_count >= 5:
        raise HTTPException(status_code=409, detail="You can create a maximum of 5 wallets")

    new_wallet = Wallet(user_id=user_id, name=wallet_name, currency=currency)
    session.add(new_wallet)
    await session.commit()
    await session.refresh(new_wallet)

    return {"name": new_wallet.name, "count": wallet_count}
    



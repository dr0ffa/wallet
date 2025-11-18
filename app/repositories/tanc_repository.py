from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException

from models_db.models import Transaction

# deposit, withdraw-вывод, transfer, refill - пополнение

async def inital_transaction(wallet_id, initial_balance, currency, session: AsyncSession):
    initial_tranc = Transaction(wallet_id=wallet_id, type="deposit", amount=initial_balance, currency=currency, status="completed")
    session.add(initial_tranc)
    await session.commit()

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from sqlalchemy.exc import NoResultFound
import uuid

from models_db.models import Mfa, User
from logging import getLogger
logger = getLogger(__name__)

async def create_mfa_record(db: AsyncSession, user_id: uuid.UUID) -> Mfa:
    new_mfa = Mfa(user_id=user_id, type=None, secret=None, enabled=False, created_at=None)
    logger.debug(f"nach {new_mfa} ")
    db.add(new_mfa)
    await db.commit()
    await db.refresh(new_mfa)
    return new_mfa

async def update_mfa_record(db: AsyncSession, user_id: uuid.UUID, secret: str, enabled) -> Mfa:
    result = await db.scalars(select(Mfa).where(Mfa.user_id == user_id))
    mfa_record = result.first()

    if not mfa_record:
        raise NoResultFound("MFA record not found for this user")

    mfa_record.secret = secret
    mfa_record.enabled = enabled
    mfa_record.type = "totp"
    mfa_record.created_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(mfa_record)
    return mfa_record

async def check_mfa(user_id, db: AsyncSession):
    mfa_record = await db.scalar(select(Mfa).where(Mfa.user_id == user_id))
    if not mfa_record:
        raise NoResultFound("MFA record not found for this user")

    return mfa_record

async def active_mfa(mfa_record, db: AsyncSession):
    mfa_record.enabled = True
    await db.commit()



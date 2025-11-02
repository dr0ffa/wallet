import pyotp
import qrcode  # type: ignore
from io import BytesIO
import base64
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from core.security import decrypt_secret


async def enable_mfa(user_id, username: str, db: AsyncSession):
    secret = pyotp.random_base32()

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name="MyApp")

    qr = qrcode.make(uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")  # type: ignore
    qr_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {"secret": secret, "qr_code": qr_b64}

async def check_totp(mfa_record, otp):
    totp = pyotp.TOTP(decrypt_secret(mfa_record.secret))
    if not totp.verify(otp):
        raise HTTPException(status_code=400, detail="Invalid or expired code")

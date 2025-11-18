from pydantic import BaseModel, Field

from models_db.models import CurrencyEnum

class CreateWalletRequest(BaseModel):
    name: str = Field(max_length=20)
    initial_balance: float=Field(0.0, ge=0.0, le=1000.0)
    currency: CurrencyEnum

class DeleteWallet(BaseModel):
    wallet_id: str = Field(max_length=50)

class RefillWallet(BaseModel):
    amount: float=Field(0.0, ge=10.0, le=100000.0)
    wallet_id: str = Field(max_length=50)
    
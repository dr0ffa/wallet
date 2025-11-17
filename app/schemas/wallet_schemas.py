from pydantic import BaseModel, Field

from models_db.models import CurrencyEnum

class CreateWalletRequest(BaseModel):
    name: str = Field(max_length=20)
    currency: CurrencyEnum 
    
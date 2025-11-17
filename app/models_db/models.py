import uuid
from enum import Enum

from datetime import datetime, timezone

from typing import List
from typing import Optional

from sqlalchemy import ForeignKey, String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SqlEnum

from models_db.database import Base


class CurrencyEnum(str, Enum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
    BTC = "BTC"
    ETH = "ETH"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=True)

    mfas: Mapped[List["Mfa"]] = relationship("Mfa", back_populates="user", cascade="all, delete-orphan")
    wallets: Mapped[List["Wallet"]] = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")


class Mfa(Base):
    __tablename__ = "mfa"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=True)
    secret: Mapped[str] = mapped_column(String(1000), nullable=True)
    enabled: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="mfas")

class Wallet(Base):
    __tablename__="wallet"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[float] = mapped_column(default=0.0, nullable=False)
    currency: Mapped[CurrencyEnum] = mapped_column(SqlEnum(CurrencyEnum), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="wallets")

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="wallet",
        cascade="all, delete-orphan",
        foreign_keys="[Transaction.wallet_id]"  # явное указание, какой FK использовать
    )

    #user: Mapped["User"] = relationship("User", back_populates="wallets")
    #transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # "deposit", "withdraw", "transfer"
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False) # валюта
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # "pending", "completed", "failed"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    related_wallet_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=True)  # для переводов между кошельками

    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        back_populates="transactions",
        foreign_keys=[wallet_id]  # обязательно указать FK
    )

    related_wallet: Mapped[Optional["Wallet"]] = relationship(
        "Wallet",
        foreign_keys=[related_wallet_id]  # это для переводов, back_populates не нужен
    )
    #wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="transactions")

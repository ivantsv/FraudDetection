from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from pydantic.networks import IPvAnyAddress

class TransactionRequest(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(...)
    sender_account: str = Field(..., min_length=5)
    receiver_account: str = Field(..., min_length=5)
    amount: float = Field(..., gt=0)
    transaction_type: str = Field(...)
    merchant_category: str = Field(...)
    location: str = Field(...)
    device_used: str = Field(...)
    payment_channel: str = Field(...)
    ip_address: IPvAnyAddress = Field(...)
    device_hash: str = Field(..., min_length=8)

    @field_validator("receiver_account")
    @classmethod
    def accounts_must_differ(cls, v, info):
        sender = info.data.get("sender_account")
        if sender and v == sender:
            raise ValueError("sender_account и receiver_account не могут совпадать")
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_not_future(cls, v: datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        if v > now:
            raise ValueError("timestamp не может быть из будущего")
        return v

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v):
        allowed = {"transfer", "payment", "withdrawal", "deposit"}
        if v not in allowed:
            raise ValueError(f"Недопустимый тип транзакции: {v}. Допустимые: {', '.join(allowed)}")
        return v

    def to_dict(self):
        return {
            **self.model_dump(),
            "timestamp": self.timestamp.isoformat(),
            "ip_address": str(self.ip_address)
        }
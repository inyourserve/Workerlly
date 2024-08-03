from pydantic import BaseModel
from typing import List
from datetime import datetime

class WalletRecharge(BaseModel):
    amount: float

class Payment(BaseModel):
    amount: float

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    type: str  # "recharge" or "payment"
    amount: float
    date: datetime

class WalletResponse(BaseModel):
    user_id: str
    balance: float
    transactions: List[Transaction]
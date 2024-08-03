import uuid
from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from app.api.v1.endpoints.users import get_current_user
from app.api.v1.schemas.wallet import (
    WalletRecharge,
    WalletResponse,
    Transaction,
    Payment,
)
from app.db.models.database import db

router = APIRouter()


@router.get(
    "/wallet", response_model=WalletResponse, dependencies=[Depends(get_current_user)]
)
async def get_wallet(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    wallet = db.wallets.find_one({"user_id": ObjectId(user_id)})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    transactions = list(db.transactions.find({"user_id": ObjectId(user_id)}))
    return WalletResponse(
        user_id=str(wallet["user_id"]),
        balance=wallet["balance"],
        transactions=[Transaction(**tx) for tx in transactions],
    )


@router.post(
    "/wallet/recharge",
    response_model=WalletResponse,
    dependencies=[Depends(get_current_user)],
)
async def recharge_wallet(
    recharge: WalletRecharge, current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    wallet = db.wallets.find_one({"user_id": ObjectId(user_id)})
    if not wallet:
        db.wallets.insert_one({"user_id": ObjectId(user_id), "balance": 0.0})
        wallet = db.wallets.find_one({"user_id": ObjectId(user_id)})

    new_balance = wallet["balance"] + recharge.amount
    db.wallets.update_one(
        {"user_id": ObjectId(user_id)}, {"$set": {"balance": new_balance}}
    )

    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "user_id": ObjectId(user_id),
        "type": "recharge",
        "amount": recharge.amount,
        "date": datetime.utcnow(),
    }
    db.transactions.insert_one(transaction)

    transactions = list(db.transactions.find({"user_id": ObjectId(user_id)}))
    return WalletResponse(
        user_id=str(wallet["user_id"]),
        balance=new_balance,
        transactions=[Transaction(**tx) for tx in transactions],
    )


@router.post(
    "/wallet/payment",
    response_model=WalletResponse,
    dependencies=[Depends(get_current_user)],
)
async def process_payment(
    payment: Payment, current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    wallet = db.wallets.find_one({"user_id": ObjectId(user_id)})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet["balance"] < payment.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    new_balance = wallet["balance"] - payment.amount
    db.wallets.update_one(
        {"user_id": ObjectId(user_id)}, {"$set": {"balance": new_balance}}
    )

    transaction = {
        "transaction_id": str(uuid.uuid4()),
        "user_id": ObjectId(user_id),
        "type": "payment",
        "amount": payment.amount,
        "date": datetime.utcnow(),
    }
    db.transactions.insert_one(transaction)

    transactions = list(db.transactions.find({"user_id": ObjectId(user_id)}))
    return WalletResponse(
        user_id=str(wallet["user_id"]),
        balance=new_balance,
        transactions=[Transaction(**tx) for tx in transactions],
    )


@router.get(
    "/wallet/transactions",
    response_model=List[Transaction],
    dependencies=[Depends(get_current_user)],
)
async def get_transactions(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    transactions = list(db.transactions.find({"user_id": ObjectId(user_id)}))
    return [Transaction(**tx) for tx in transactions]

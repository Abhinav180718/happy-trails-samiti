from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
from typing import Optional

app = FastAPI(title="Happy Trails Samiti API", version="0.1.0")


@app.get("/")
def root():
    return {
        "status": "online",
        "application": "Happy Trails Samiti",
        "message": "Happy Trails Samiti API is running"
    }

class Transaction(BaseModel):
    transaction_type: str
    category: str
    name: str
    flat_number: Optional[str] = None
    amount: float
    payment_mode: Optional[str] = None
    utr: Optional[str] = None
    remarks: Optional[str] = None

transactions = []

@app.get("/health")
def health():
    return {"status": "ok", "application": "Happy Trails Samiti"}

@app.get("/api/transactions")
def get_transactions():
    return transactions

@app.post("/api/transactions")
def add_transaction(transaction: Transaction):
    item = transaction.model_dump()
    item["id"] = f"HT-{len(transactions)+1:05d}"
    item["date"] = str(date.today())
    transactions.append(item)
    return item

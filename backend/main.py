import os
from datetime import date
from typing import Optional


from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI(
    title="Happy Trails Samiti API",
    version="0.3.0"
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not configured")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


@app.get("/")
def root():
    return {
        "status": "online",
        "application": "Happy Trails Samiti",
        "message": "Happy Trails Samiti API is running"
    }


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

@app.get("/app")
def app_page():
    return FileResponse("frontend/index.html")


@app.get("/api/dashboard")
def dashboard():

    try:
        with engine.connect() as connection:

            income = connection.execute(
                text("""
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE transaction_type = 'income'
                """)
            ).scalar() or 0

            expenses = connection.execute(
                text("""
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE transaction_type = 'expense'
                """)
            ).scalar() or 0

            committed = connection.execute(
                text("""
                    SELECT COALESCE(SUM(committed_amount), 0)
                    FROM sponsorships
                """)
            ).scalar() or 0

            received = connection.execute(
                text("""
                    SELECT COALESCE(SUM(received_amount), 0)
                    FROM sponsorships
                """)
            ).scalar() or 0

            return {
                "total_income": float(income),
                "total_expenses": float(expenses),
                "balance": float(income - expenses),
                "sponsorship_committed": float(committed),
                "sponsorship_received": float(received),
                "sponsorship_pending": float(committed - received)
            }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard query failed: {str(e)}"
        )


@app.get("/api/transactions")
def get_transactions():

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("""
                    SELECT
                        id,
                        transaction_ref,
                        transaction_date,
                        transaction_type,
                        category,
                        name_or_vendor,
                        flat_number,
                        amount,
                        payment_mode,
                        utr,
                        remarks
                    FROM transactions
                    ORDER BY transaction_date DESC, id DESC
                """)
            )

            return [
                dict(row._mapping)
                for row in result
            ]

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve transactions: {str(e)}"
        )


class Transaction(BaseModel):

    transaction_type: str
    category: str
    name: str
    flat_number: Optional[str] = None
    amount: float
    payment_mode: Optional[str] = None
    utr: Optional[str] = None
    remarks: Optional[str] = None


@app.post("/api/transactions")
def add_transaction(transaction: Transaction):

    if transaction.transaction_type not in ["income", "expense"]:
        raise HTTPException(
            status_code=400,
            detail="transaction_type must be income or expense"
        )

    if transaction.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero"
        )

    try:

        with engine.begin() as connection:

            next_id = connection.execute(
                text("""
                    SELECT COALESCE(MAX(id), 0) + 1
                    FROM transactions
                """)
            ).scalar()

            transaction_ref = f"HT-{int(next_id):05d}"

            result = connection.execute(
                text("""
                    INSERT INTO transactions (
                        transaction_ref,
                        transaction_date,
                        transaction_type,
                        category,
                        name_or_vendor,
                        flat_number,
                        amount,
                        payment_mode,
                        utr,
                        remarks
                    )
                    VALUES (
                        :transaction_ref,
                        :transaction_date,
                        :transaction_type,
                        :category,
                        :name_or_vendor,
                        :flat_number,
                        :amount,
                        :payment_mode,
                        :utr,
                        :remarks
                    )
                    RETURNING id, transaction_ref
                """),
                {
                    "transaction_ref": transaction_ref,
                    "transaction_date": date.today(),
                    "transaction_type": transaction.transaction_type,
                    "category": transaction.category,
                    "name_or_vendor": transaction.name,
                    "flat_number": transaction.flat_number,
                    "amount": transaction.amount,
                    "payment_mode": transaction.payment_mode,
                    "utr": transaction.utr,
                    "remarks": transaction.remarks
                }
            )

            row = result.fetchone()

            return {
                "status": "success",
                "id": row.id,
                "transaction_ref": row.transaction_ref
            }

    except SQLAlchemyError as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to save transaction: {str(e)}"
        )

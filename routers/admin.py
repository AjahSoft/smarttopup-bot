from fastapi import APIRouter
from models import SessionLocal, Transaction

router = APIRouter()

@router.get("/transactions")
def list_transactions():
    db = SessionLocal()
    txs = db.query(Transaction).all()
    db.close()
    return [{"id": t.id, "user": t.user_id, "service": t.service, "amount": t.amount, "status": t.status} for t in txs]

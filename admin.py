from fastapi import APIRouter
from models import SessionLocal, Transaction

router = APIRouter()

@router.get("/transactions")
async def admin_transactions():
    db = SessionLocal()
    try:
        txs = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(200).all()
        out = []
        for t in txs:
            out.append({
                "id": t.id, "user": t.user_whatsapp, "type": t.tx_type, "amount": t.amount,
                "status": t.status, "ref": t.provider_ref, "created_at": t.created_at.isoformat()
            })
        return out
    finally:
        db.close()

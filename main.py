<<<<<<< HEAD
from fastapi import FastAPI
from routers import messages, admin
from models import Base, engine

app = FastAPI(title="SmartTopUp Bot API")

Base.metadata.create_all(bind=engine)

app.include_router(messages.router, prefix="/webhook", tags=["WhatsApp Webhook"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Panel"])

@app.get("/")
def home():
    return {"message": "SmartTopUp Bot API is running 🚀"}
=======
"""SmartTopUp - FastAPI entrypoint

Run:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from routers import messages, admin
from models import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartTopUp WhatsApp VTU Bot (FastAPI)")

app.include_router(messages.router, prefix="")
app.include_router(admin.router, prefix="/admin")

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "SmartTopUp WhatsApp VTU Bot (FastAPI) is running."
>>>>>>> 1a5d991645014bfafd0087e836585a6455805ddd

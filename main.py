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

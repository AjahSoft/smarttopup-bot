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

"""
whatsapp_client.py

Simple WhatsApp Cloud API helper.
"""
import httpx
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    WA_TOKEN: str = Field("YOUR_WHATSAPP_CLOUD_API_TOKEN", env="WA_TOKEN")
    WA_PHONE_NUMBER_ID: str = Field("YOUR_PHONE_NUMBER_ID", env="WA_PHONE_NUMBER_ID")
    class Config:
        env_file = ".env"

settings = Settings()

WA_URL_TEMPLATE = f"https://graph.facebook.com/v17.0/{settings.WA_PHONE_NUMBER_ID}/messages"

async def send_whatsapp_text(to_whatsapp_id: str, message: str):
    headers = {
        "Authorization": f"Bearer {settings.WA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_whatsapp_id,
        "type": "text",
        "text": {"body": message}
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(WA_URL_TEMPLATE, headers=headers, json=payload)
        if resp.status_code >= 400:
            print("WhatsApp send failed:", resp.status_code, resp.text)
        try:
            return resp.json()
        except Exception:
            return {"error": resp.text}

<<<<<<< HEAD
import requests
import os

WHATSAPP_API_URL = "https://graph.facebook.com/v17.0"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "your_phone_number_id")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "your_access_token")

def send_message(to, text):
    url = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
=======
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
>>>>>>> 1a5d991645014bfafd0087e836585a6455805ddd
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
<<<<<<< HEAD
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
=======
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
>>>>>>> 1a5d991645014bfafd0087e836585a6455805ddd

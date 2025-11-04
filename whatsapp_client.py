import requests
import os

WHATSAPP_API_URL = "https://graph.facebook.com/v17.0"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "your_phone_number_id")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "your_access_token")

def send_message(to, text):
    url = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

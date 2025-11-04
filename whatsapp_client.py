import requests
import os

WHATSAPP_API_URL = "https://graph.facebook.com/v19.0/{}/messages".format(os.getenv("PHONE_NUMBER_ID"))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def send_message(phone_number: str, message: str):
    """Send a text message via WhatsApp Cloud API."""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print("Error sending message:", response.text)
    return response.json()

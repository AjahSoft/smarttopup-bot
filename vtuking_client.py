import requests
import os

VTUKING_BASE_URL = os.getenv("VTUKING_BASE_URL", "https://vtuking.ng/api/")
VTUKING_API_KEY = os.getenv("VTUKING_API_KEY", "your_api_key_here")

def buy_airtime(network, phone, amount):
    payload = {
        "api_key": VTUKING_API_KEY,
        "network": network,
        "phone": phone,
        "amount": amount
    }
    try:
        res = requests.post(f"{VTUKING_BASE_URL}/airtime", json=payload, timeout=10)
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

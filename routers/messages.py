from fastapi import APIRouter, Request
from whatsapp_client import send_message
from vtuking_client import buy_airtime

router = APIRouter()

@router.post("/")
async def webhook(request: Request):
    data = await request.json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = msg["from"]
        text = msg["text"]["body"].lower()

        if "airtime" in text:
            send_message(sender, "Please send the network, phone, and amount (e.g., MTN 08012345678 500).")
        elif any(net in text for net in ["mtn", "glo", "airtel", "9mobile"]):
            parts = text.split()
            result = buy_airtime(parts[0], parts[1], parts[2])
            send_message(sender, f"Processing your {parts[0]} recharge of ₦{parts[2]} for {parts[1]}...\n\nResponse: {result}")
        else:
            send_message(sender, "Welcome to SmartTopUp! Type 'airtime' to begin.")
    except Exception as e:
        print("Webhook error:", e)
    return {"status": "received"}

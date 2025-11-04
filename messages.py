from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from models import User, Transaction, SessionLocal
from whatsapp_client import send_whatsapp_text
from vtuking_client import VTUKingClient, VTUResponse
from datetime import datetime
import json
from pydantic import BaseSettings, Field

router = APIRouter()

class Settings(BaseSettings):
    VTUKING_BASE_URL: str = Field("https://api.vtuking.placeholder", env="VTUKING_BASE_URL")
    VTUKING_API_KEY: str = Field("VTUKING_API_KEY_PLACEHOLDER", env="VTUKING_API_KEY")
    VERIFY_TOKEN: str = Field("whatsapp_verify_token", env="VERIFY_TOKEN")
    ADMIN_WHATSAPP: str = Field("2348012345678", env="ADMIN_WHATSAPP")
    class Config:
        env_file = ".env"

settings = Settings()
vtuking = VTUKingClient(settings.VTUKING_BASE_URL, settings.VTUKING_API_KEY)

def normalize_phone(num: str) -> str:
    num = num.strip().replace("+", "")
    if num.startswith("0"):
        return "234" + num[1:]
    if num.startswith("234"):
        return num
    return num

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def MENU_TEXT():
    return (
        "👋 Welcome to SmartTopUp!\n\n"
        "Send one of the commands below:\n"
        "• Menu / Start / Hi - Show this menu\n"
        "• Buy airtime <network> <amount> <phone>\n"
        "  e.g. Buy airtime MTN 500 08031234567\n"
        "• Buy data <network> <plan_code> <phone>\n"
        "  e.g. Buy data MTN 1GB 08031234567\n"
        "• Pay bill <phcn|dstv|gotv|startimes> <account> <amount>\n"
        "  e.g. Pay bill phcn 1234567890 5000\n"
        "• Buy pin <waec|jamb> <qty>\n"
        "• Fund <amount>\n"
        "• Balance - check wallet balance\n"
        "\nNeed help? Reply 'Support'\n"
    )

@router.get("/webhook")
async def webhook_verify(hub_mode: str = None, hub_verify_token: str = None, hub_challenge: str = None):
    if hub_verify_token == settings.VERIFY_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Invalid verify token")

@router.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return {"status":"no_message"}
        msg = messages[0]
        wa_from = msg.get("from")
        if msg.get("type") == "text":
            wa_text = msg["text"]["body"]
        elif msg.get("type") == "button":
            wa_text = msg["button"]["text"]
        else:
            wa_text = msg.get("text", {}).get("body", "") or msg.get("type")
        background_tasks.add_task(process_incoming_message, wa_from, wa_text)
        return {"status":"queued"}
    except Exception as e:
        print("Webhook parse error:", e)
        return {"status":"error", "detail": str(e)}

async def process_incoming_message(whatsapp_id: str, text: str):
    db = next(get_db())
    wnum = normalize_phone(whatsapp_id)
    user = db.query(User).filter(User.whatsapp_id == wnum).first()
    if not user:
        user = User(whatsapp_id=wnum, name=None, wallet=0.0)
        db.add(user)
        db.commit()
        db.refresh(user)

    text_clean = text.strip().lower()
    if text_clean in ("hi","hello","menu","start"):
        await send_whatsapp_text(wnum, MENU_TEXT())
        return

    if text_clean.startswith("buy airtime"):
        parts = text_clean.split()
        try:
            _, _, network, amount_str, phone = parts[:5]
        except ValueError:
            await send_whatsapp_text(wnum, "To buy airtime: send `Buy airtime <network> <amount> <phone>`\\nExample: Buy airtime MTN 500 08031234567")
            return
        try:
            amount = float(amount_str)
        except:
            await send_whatsapp_text(wnum, "Invalid amount. Use numbers only.")
            return
        phone_norm = normalize_phone(phone)
        tx = Transaction(user_whatsapp=wnum, tx_type="airtime", provider="vtuking", amount=amount, charge=0.0, status="processing", created_at=datetime.utcnow())
        db.add(tx); db.commit(); db.refresh(tx)
        resp = await vtuking.send_airtime(network.upper(), phone_norm, amount)
        if resp.success:
            tx.status = "success"; tx.provider_ref = resp.provider_ref; tx.charge = 10.0
            tx.meta = json.dumps({"provider_message": resp.message})
            db.add(tx); db.commit()
            await send_whatsapp_text(wnum, format_receipt(tx))
        else:
            tx.status = "failed"; tx.meta = json.dumps({"error": resp.message})
            db.add(tx); db.commit()
            await send_whatsapp_text(wnum, f"❌ Airtime failed: {resp.message}")
        return

    if text_clean.startswith("buy data"):
        parts = text_clean.split()
        try:
            _, _, network, plan, phone = parts[:5]
        except ValueError:
            await send_whatsapp_text(wnum, "To buy data: `Buy data <network> <plan_code> <phone>`\\nExample: Buy data MTN 1GB 08031234567")
            return
        phone_norm = normalize_phone(phone)
        tx = Transaction(user_whatsapp=wnum, tx_type="data", provider="vtuking", amount=0.0, status="processing", created_at=datetime.utcnow(), meta=json.dumps({"plan": plan}))
        db.add(tx); db.commit(); db.refresh(tx)
        resp = await vtuking.send_data(network.upper(), phone_norm, plan)
        if resp.success:
            tx.status = "success"; tx.provider_ref = resp.provider_ref; tx.charge = 40.0
            db.add(tx); db.commit()
            await send_whatsapp_text(wnum, format_receipt(tx))
        else:
            tx.status = "failed"; tx.meta = json.dumps({"error": resp.message})
            db.add(tx); db.commit()
            await send_whatsapp_text(wnum, f"❌ Data purchase failed: {resp.message}")
        return

    if text_clean.startswith("pay bill") or text_clean.startswith("pay electricity") or text_clean.startswith("pay tv"):
        parts = text_clean.split()
        try:
            if parts[1] in ("phcn","dstv","gotv","startimes"):
                bill_type = parts[1]; acct = parts[2]; amount = float(parts[3])
            else:
                await send_whatsapp_text(wnum, "To pay a bill send: `Pay bill <phcn|dstv|gotv|startimes> <account> <amount>`")
                return
        except Exception:
            await send_whatsapp_text(wnum, "Invalid bill command. Format: `Pay bill <phcn|dstv|gotv|startimes> <account> <amount>`")
            return
        tx = Transaction(user_whatsapp=wnum, tx_type="bill", provider="vtuking", amount=amount, status="processing", created_at=datetime.utcnow(), meta=json.dumps({"account": acct, "bill_type": bill_type}))
        db.add(tx); db.commit(); db.refresh(tx)
        resp = await vtuking.pay_bill(bill_type.upper(), acct, amount)
        if resp.success:
            tx.status = "success"; tx.provider_ref = resp.provider_ref; tx.charge = 100.0
            db.add(tx); db.commit()
            await send_whatsapp_text(wnum, format_receipt(tx))
        else:
            tx.status = "failed"; tx.meta = json.dumps({"error": resp.message})
            db.add(tx); db.commit()
            await send_whatsapp_text(wnum, f"❌ Bill payment failed: {resp.message}")
        return

    if text_clean.startswith("buy pin"):
        parts = text_clean.split()
        try:
            _, _, pin_type, qty_str = parts[:4]; qty = int(qty_str)
        except Exception:
            await send_whatsapp_text(wnum, "To buy PINs: `Buy pin <waec|jamb> <qty>`\\nExample: Buy pin waec 2")
            return
        tx = Transaction(user_whatsapp=wnum, tx_type="pin", provider="vtuking", amount=0.0, status="processing", created_at=datetime.utcnow(), meta=json.dumps({"pin_type": pin_type, "qty": qty}))
        db.add(tx); db.commit(); db.refresh(tx)
        resp = await vtuking.buy_pin(pin_type.upper(), qty)
        if resp.success:
            tx.status = "success"; tx.provider_ref = resp.provider_ref; tx.charge = 200.0; tx.meta = resp.message
            db.add(tx); db.commit()
            await send_whatsapp_text(wnum, f"✅ PINs delivered:\\n{resp.message}")
        else:
            tx.status = "failed"; tx.meta = json.dumps({"error": resp.message})
            db.add(tx); db.commit()
            await send_whatsapp_text(wnum, f"❌ PIN purchase failed: {resp.message}")
        return

    if text_clean.startswith("fund") or text_clean.startswith("fund wallet"):
        parts = text_clean.split()
        try:
            amount = float(parts[1])
        except Exception:
            await send_whatsapp_text(wnum, "To fund wallet: `Fund <amount>`\\nExample: Fund 2000")
            return
        tx = Transaction(user_whatsapp=wnum, tx_type="fund", provider="paystack/monnify", amount=amount, status="pending", created_at=datetime.utcnow())
        db.add(tx); db.commit(); db.refresh(tx)
        await send_whatsapp_text(wnum, f"To fund ₦{amount}, please pay using the payment link (placeholder). We will auto-credit on verification.")
        return

    if text_clean.startswith("balance") or text_clean.startswith("check balance"):
        await send_whatsapp_text(wnum, f"💰 Wallet balance: ₦{user.wallet:.2f}")
        return

    await send_whatsapp_text(wnum, "Sorry, I didn't understand that. Send 'Menu' to see options.")

def format_receipt(tx):
    return (
        f"✅ Transaction {tx.status.upper()}!\\n"
        f"Type: {tx.tx_type}\\n"
        f"Amount: ₦{tx.amount}\\n"
        f"Your Profit: ₦{tx.charge}\\n"
        f"Ref: {tx.provider_ref or 'N/A'}\\n"
        f"Time: {tx.created_at.isoformat()}"
    )

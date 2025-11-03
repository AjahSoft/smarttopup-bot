"""
vtuking_client.py

Placeholder VTUKing client. Replace endpoints and parsing with real VTUKing docs.
"""
import httpx
from pydantic import BaseModel
from typing import Optional

class VTUResponse(BaseModel):
    success: bool
    provider_ref: Optional[str]
    message: Optional[str] = None

class VTUKingClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def send_airtime(self, network: str, phone: str, amount: float) -> VTUResponse:
        url = f"{self.base_url}/airtime"
        payload = {"network": network, "phone": phone, "amount": amount}
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            try:
                data = r.json()
            except Exception:
                return VTUResponse(success=False, provider_ref=None, message=f"Invalid response: {r.text}")
            if r.status_code in (200,201) and data.get("status") in ("success","ok"):
                return VTUResponse(success=True, provider_ref=data.get("ref") or data.get("transaction_id"), message=data.get("message"))
            return VTUResponse(success=False, provider_ref=None, message=data.get("message") or r.text)

    async def send_data(self, network: str, phone: str, plan_code: str) -> VTUResponse:
        url = f"{self.base_url}/data"
        payload = {"network": network, "phone": phone, "plan": plan_code}
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            try:
                data = r.json()
            except Exception:
                return VTUResponse(success=False, provider_ref=None, message=f"Invalid response: {r.text}")
            if r.status_code in (200,201) and data.get("status") in ("success","ok"):
                return VTUResponse(success=True, provider_ref=data.get("ref") or data.get("transaction_id"), message=data.get("message"))
            return VTUResponse(success=False, provider_ref=None, message=data.get("message") or r.text)

    async def pay_bill(self, bill_type: str, account: str, amount: float) -> VTUResponse:
        url = f"{self.base_url}/bills"
        payload = {"type": bill_type, "account": account, "amount": amount}
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            try:
                data = r.json()
            except Exception:
                return VTUResponse(success=False, provider_ref=None, message=f"Invalid response: {r.text}")
            if r.status_code in (200,201) and data.get("status") in ("success","ok"):
                return VTUResponse(success=True, provider_ref=data.get("ref") or data.get("transaction_id"), message=data.get("message"))
            return VTUResponse(success=False, provider_ref=None, message=data.get("message") or r.text)

    async def buy_pin(self, pin_type: str, quantity: int) -> VTUResponse:
        url = f"{self.base_url}/pins"
        payload = {"type": pin_type, "qty": quantity}
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            try:
                data = r.json()
            except Exception:
                return VTUResponse(success=False, provider_ref=None, message=f"Invalid response: {r.text}")
            if r.status_code in (200,201) and data.get("status") in ("success","ok"):
                return VTUResponse(success=True, provider_ref=data.get("ref") or data.get("transaction_id"), message=str(data.get("pins", [])))
            return VTUResponse(success=False, provider_ref=None, message=data.get("message") or r.text)

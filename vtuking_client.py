"""
vtuking_client.py

VTUKing API client for SmartTopUp Bot.
Supports airtime, data, bills, and PIN purchases.
"""

import os
import httpx
from pydantic import BaseModel
from typing import Optional

# Load environment variables
VTUKING_BASE_URL = os.getenv("VTUKING_BASE_URL", "https://vtuking.ng/api")
VTUKING_API_KEY = os.getenv("VTUKING_API_KEY", "your_api_key_here")


class VTUResponse(BaseModel):
    success: bool
    provider_ref: Optional[str]
    message: Optional[str] = None


class VTUKingClient:
    """Async VTUKing API client"""

    def __init__(self, base_url: str = VTUKING_BASE_URL, api_key: str = VTUKING_API_KEY):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def send_airtime(self, network: str, phone: str, amount: float) -> VTUResponse:
        """Buy airtime"""
        url = f"{self.base_url}/airtime"
        payload = {"network": network, "phone": phone, "amount": amount}

        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            return self._parse_response(r)

    async def send_data(self, network: str, phone: str, plan_code: str) -> VTUResponse:
        """Buy data bundle"""
        url = f"{self.base_url}/data"
        payload = {"network": network, "phone": phone, "plan": plan_code}

        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            return self._parse_response(r)

    async def pay_bill(self, bill_type: str, account: str, amount: float) -> VTUResponse:
        """Pay bills like electricity, cable TV, etc."""
        url = f"{self.base_url}/bills"
        payload = {"type": bill_type, "account": account, "amount": amount}

        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            return self._parse_response(r)

    async def buy_pin(self, pin_type: str, quantity: int) -> VTUResponse:
        """Buy recharge pins (bulk or single)"""
        url = f"{self.base_url}/pins"
        payload = {"type": pin_type, "qty": quantity}

        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            return self._parse_response(r)

    def _parse_response(self, r: httpx.Response) -> VTUResponse:
        """Internal helper to parse VTUKing API responses"""
        try:
            data = r.json()
        except Exception:
            return VTUResponse(success=False, provider_ref=None, message=f"Invalid response: {r.text}")

        if r.status_code in (200, 201) and data.get("status") in ("success", "ok"):
            return VTUResponse(
                success=True,
                provider_ref=data.get("ref") or data.get("transaction_id"),
                message=data.get("message"),
            )
        return VTUResponse(success=False, provider_ref=None, message=data.get("message") or r.text)


# Optional: backward-compatible helper for simple use
async def buy_airtime(network: str, phone: str, amount: float) -> dict:
    """Quick async helper function"""
    client = VTUKingClient()
    result = await client.send_airtime(network, phone, amount)
    return result.dict()

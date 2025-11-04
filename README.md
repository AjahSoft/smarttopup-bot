# SmartTopUp - WhatsApp VTU Bot (FastAPI)

This repo contains a multi-file FastAPI project for a WhatsApp-based VTU (airtime, data, bills, exam pins) bot.
It is based on the single-file prototype and split into maintainable modules.

## Structure
- `main.py` - FastAPI entrypoint
- `models.py` - SQLAlchemy models and DB setup
- `vtuking_client.py` - VTU provider client (placeholder)
- `whatsapp_client.py` - WhatsApp Cloud API helper
- `routers/messages.py` - webhook handlers and message processing logic
- `routers/admin.py` - simple admin routes
- `.env.example` - example env vars

## Quick start
1. Copy `.env.example` to `.env` and fill with real credentials.
2. Install deps:
   ```
   pip install -r requirements.txt
   ```
3. Run:
   ```
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Expose local server (ngrok) and set webhook URL in Facebook Developer Dashboard to:
   `https://<your-host>/webhook`

## Notes
- VTUKing client uses placeholder endpoints. Replace with real VTUKing API details.
- Implement payment link generation and webhook verification for Paystack/Monnify.
- Improve conversation state handling for production (use Redis or DB session state).

# Telegram UPI/Paytm Subscription Bot (Example)


**Features**
- aiogram-based Telegram bot
- FastAPI payment page showing a UPI deep-link QR for scanning
- SQLite persistence for users, orders, and subscriptions
- Webhook endpoint to accept payment confirmations (mockable for testing)
- Automatic expiry handling with APScheduler
- Example of creating and revoking chat invite links


**Warning:** This repo is a template/example. Real payment integration (Paytm/UPI merchant APIs) must be implemented using the provider's signed callbacks and credentials.


## Quickstart (development)


1. Copy `.env.example` to `.env` and fill values (BOT_TOKEN, MERCHANT_UPI, CHANNEL_ID, WEBHOOK_SECRET)
2. Create a Python virtualenv and install requirements:


```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

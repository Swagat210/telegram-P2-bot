from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
import qrcode
import io
from ..bot.db import init_db, mark_order_paid, create_order
from ..bot.payments import create_upi_pay_link, generate_order_id
from ..bot.config import WEBHOOK_SECRET
from pathlib import Path
import base64

app = FastAPI()

TEMPLATE = """
<!doctype html>
<html>
<head><meta charset='utf-8'><title>Pay</title></head>
<body>
<h2>Complete Your Payment</h2>
<p>Order: {{order_id}} — Amount: ₹{{amount}}</p>
<p>Scan this QR with any UPI app, or click the link to open UPI apps on mobile:</p>
<img src='data:image/png;base64,{{qr_base64}}'/>
<p><a href='{{upi_link}}'>Open UPI app</a></p>
<p>After you've paid, the payment gateway should POST to /webhook to confirm the payment (for testing, you can hit the webhook yourself).</p>
</body></html>
"""

@app.on_event('startup')
async def startup():
    await init_db()

@app.get('/pay/{order_id}', response_class=HTMLResponse)
async def pay_page(order_id: str):
    # In production you'd fetch order details; for demonstration assume amount=99
    # We will create a placeholder UPI link derived from the order
    amount = 99.00
    upi_link, _ = create_upi_pay_link(order_id, amount)
    # create QR
    img = qrcode.make(upi_link)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    html = Template(TEMPLATE).render(order_id=order_id, amount=f"{amount:.2f}", qr_base64=qr_b64, upi_link=upi_link)
    return HTMLResponse(content=html)

@app.post('/webhook')
async def webhook(request: Request):
    # Simple webhook expecting json with order_id and secret
    data = await request.json()
    secret = data.get('secret')
    order_id = data.get('order_id')
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail='Invalid secret')
    # Mark order paid
    res = await mark_order_paid(order_id)
    if not res:
        raise HTTPException(status_code=404, detail='Order not found')
    # Optionally: notify bot by writing to DB (bot polls DB) or send direct HTTP request to bot webhook
    return {'status': 'ok'}

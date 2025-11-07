from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = environ.get('BOT_TOKEN', "8266443596:AAE-ziq6rRzR0zZ1Ga5Ubgq2JO6M_eTjS2k")
MERCHANT_UPI = os.getenv('8260758004@ptsbi')
CHANNEL_ID = os.getenv('3059982885')
WEBHOOK_SECRET = os.getenv('mysupersecret123')
HOST = os.getenv('HOST', 'http://localhost:5611')
DB_PATH = Path(__file__).parent.parent / 'data' / 'bot.db'

---

## bot/db.py

```python
import aiosqlite
from datetime import datetime, timedelta
from pathlib import Path
from .config import DB_PATH

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

CREATE_SQL = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    username TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY,
    name TEXT,
    days INTEGER,
    price REAL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE,
    telegram_id INTEGER,
    plan_id INTEGER,
    amount REAL,
    status TEXT,
    created_at TEXT,
    paid_at TEXT,
    expiry_at TEXT,
    pay_link TEXT
);
'''

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_SQL)
        # Insert sample plans if not exists
        await db.execute("INSERT OR IGNORE INTO plans (id, name, days, price) VALUES (1, 'Movies Only (1 Month)', 30, 99.00)")
        await db.execute("INSERT OR IGNORE INTO plans (id, name, days, price) VALUES (2, 'Adult Only (1 Month)', 30, 149.00)")
        await db.execute("INSERT OR IGNORE INTO plans (id, name, days, price) VALUES (3, 'Movies+Adult (1 Month)', 30, 199.00)")
        await db.commit()

async def create_order(order_id, telegram_id, plan_id, amount, pay_link):
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO orders (order_id, telegram_id, plan_id, amount, status, created_at, pay_link) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (order_id, telegram_id, plan_id, amount, 'pending', now, pay_link)
        )
        await db.commit()

async def mark_order_paid(order_id):
    now = datetime.utcnow()
    async with aiosqlite.connect(DB_PATH) as db:
        # get order
        cur = await db.execute('SELECT telegram_id, plan_id FROM orders WHERE order_id=?', (order_id,))
        row = await cur.fetchone()
        if not row:
            return None
        telegram_id, plan_id = row
        # get plan days
        cur = await db.execute('SELECT days FROM plans WHERE id=?', (plan_id,))
        plan = await cur.fetchone()
        days = plan[0] if plan else 30
        expiry = (now + timedelta(days=days)).isoformat()
        await db.execute('UPDATE orders SET status=?, paid_at=?, expiry_at=? WHERE order_id=?', ('paid', now.isoformat(), expiry, order_id))
        await db.commit()
        return {'telegram_id': telegram_id, 'expiry_at': expiry}

async def get_pending_orders():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT order_id, telegram_id FROM orders WHERE status='pending'")
        return await cur.fetchall()

async def get_expired_subscriptions():
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT order_id, telegram_id FROM orders WHERE status='paid' AND expiry_at < ?", (now,))
        return await cur.fetchall()

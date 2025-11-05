import aiosqlite
CREATE_SUBS = '''
CREATE TABLE IF NOT EXISTS subscriptions (
id INTEGER PRIMARY KEY AUTOINCREMENT,
telegram_id INTEGER,
expires_at TEXT
);
'''


async def init_db():
async with aiosqlite.connect(DB_PATH) as db:
await db.execute(CREATE_USERS)
await db.execute(CREATE_ORDERS)
await db.execute(CREATE_SUBS)
await db.commit()


async def add_user(telegram_id, username=None, first_name=None, last_name=None):
async with aiosqlite.connect(DB_PATH) as db:
cur = await db.execute("INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name) VALUES (?,?,?,?)",
(telegram_id, username, first_name, last_name))
await db.commit()


async def create_order(order_id, telegram_id, amount, status='created'):
created_at = datetime.utcnow().isoformat()
async with aiosqlite.connect(DB_PATH) as db:
await db.execute("INSERT INTO orders (order_id, telegram_id, amount, status, created_at) VALUES (?,?,?,?,?)",
(order_id, telegram_id, amount, status, created_at))
await db.commit()


async def set_order_status(order_id, status):
async with aiosqlite.connect(DB_PATH) as db:
await db.execute("UPDATE orders SET status=? WHERE order_id=?", (status, order_id))
await db.commit()


async def get_order(order_id):
async with aiosqlite.connect(DB_PATH) as db:
cur = await db.execute("SELECT order_id, telegram_id, amount, status, created_at FROM orders WHERE order_id=?", (order_id,))
row = await cur.fetchone()
return row


async def add_subscription(telegram_id, days):
expires = (datetime.utcnow() + timedelta(days=days)).isoformat()
async with aiosqlite.connect(DB_PATH) as db:
await db.execute("INSERT INTO subscriptions (telegram_id, expires_at) VALUES (?,?)", (telegram_id, expires))
await db.commit()


async def get_subscription(telegram_id):
async with aiosqlite.connect(DB_PATH) as db:
cur = await db.execute("SELECT id, expires_at FROM subscriptions WHERE telegram_id=? ORDER BY expires_at DESC LIMIT 1", (telegram_id,))
row = await cur.fetchone()
return row


async def expire_subscriptions():
now = datetime.utcnow().isoformat()
async with aiosqlite.connect(DB_PATH) as db:
await db.execute("DELETE FROM subscriptions WHERE expires_at <= ?", (now,))
await db.commit()


# helper for debugging
async def list_subscriptions():
async with aiosqlite.connect(DB_PATH) as db:
cur = await db.execute("SELECT telegram_id, expires_at FROM subscriptions")
rows = await cur.fetchall()
return rows

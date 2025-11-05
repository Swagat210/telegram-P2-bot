import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from .config import BOT_TOKEN, HOST, CHANNEL_ID
from .db import init_db, create_order, mark_order_paid
from .payments import generate_order_id, create_upi_pay_link
from .tasks import start_scheduler

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Buy Movies (₹99)', callback_data='buy_1'))
    await message.answer('Welcome! Choose a plan:', reply_markup=kb)

@dp.callback_query(lambda c: c.data and c.data.startswith('buy_'))
async def process_buy(cb: types.CallbackQuery):
    plan_id = int(cb.data.split('_')[1])
    order_id = generate_order_id()
    # price lookup simplified
    amount = 99.00
    upi_link, pay_page = create_upi_pay_link(order_id, amount)
    # create order in DB with pay page
    await create_order(order_id, cb.from_user.id, plan_id, amount, pay_page)
    # Reply with pay button
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Pay Now', url=pay_page))
    await cb.message.answer('Payment details:\nPlan: Movies Only (1 Month)\nAmount: ₹99.00\nOrder ID: ' + order_id, reply_markup=kb)
    await cb.answer()

async def notify_user_payment(telegram_id, order_id, expiry_at):
    # create invite link for channel and send
    text = f'✅ Payment received! Your order {order_id} is active until {expiry_at}. Here is your join link.'
    # create chat invite link (requires bot admin in channel)
    try:
        invite = await bot.create_chat_invite_link(chat_id=CHANNEL_ID, member_limit=1)
        text += '\n' + invite.invite_link
    except Exception as e:
        text += '\n(Unable to create invite link — make sure bot is admin in the channel)'
    await bot.send_message(telegram_id, text)

async def poll_paid_orders():
    # naive polling: check DB for orders that changed to paid and notify
    import aiosqlite
    from .db import get_pending_orders
    while True:
        # In real design use event-driven approach; here we check paid orders table
        async with aiosqlite.connect(str(__import__('pathlib').Path(__file__).parent.parent / 'data' / 'bot.db')) as db:
            cur = await db.execute("SELECT order_id, telegram_id, expiry_at FROM orders WHERE status='paid' AND notified IS NULL")
            rows = await cur.fetchall()
            for order_id, telegram_id, expiry_at in rows:
                await notify_user_payment(telegram_id, order_id, expiry_at)
                await db.execute("UPDATE orders SET notified=1 WHERE order_id=?", (order_id,))
            await db.commit()
        await asyncio.sleep(5)

async def main():
    await init_db()
    # start scheduler to expire subscriptions
    asyncio.create_task(start_scheduler(bot))
    # start long-polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

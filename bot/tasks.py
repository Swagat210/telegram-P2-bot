from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .db import get_expired_subscriptions
from datetime import datetime

async def start_scheduler(bot):
    sched = AsyncIOScheduler()

    async def check_expiry():
        rows = await get_expired_subscriptions()
        for order_id, telegram_id in rows:
            try:
                # remove user from channel if bot has rights
                await bot.ban_chat_member(chat_id=bot['config'].CHANNEL_ID, user_id=telegram_id)
                await bot.unban_chat_member(chat_id=bot['config'].CHANNEL_ID, user_id=telegram_id)
                await bot.send_message(telegram_id, 'Your subscription has expired and access was removed.')
            except Exception:
                # fallback: just notify
                await bot.send_message(telegram_id, 'Your subscription has expired.')

    sched.add_job(check_expiry, 'interval', minutes=5)
    sched.start()

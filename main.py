from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from fastapi import FastAPI

BOT_TOKEN = "8266443596:AAE-ziq6rRzR0zZ1Ga5Ubgq2JO6M_eTjS2k"
WEBHOOK_URL = "https://w-f4v4.onrender.com/webhook"

app = FastAPI()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    await message.answer("Hello! The Paytm UPI subscription bot is working!")

@app.post("/webhook")
async def telegram_webhook(update: dict):
    from aiogram import types
    update = types.Update(**update)
    await dp.process_update(update)
    return {"ok": True}
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

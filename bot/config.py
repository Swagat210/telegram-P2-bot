from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
MERCHANT_UPI = os.getenv('MERCHANT_UPI')
CHANNEL_ID = os.getenv('CHANNEL_ID')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
HOST = os.getenv('HOST', 'http://localhost:5611')
DB_PATH = Path(__file__).parent.parent / 'data' / 'bot.db'

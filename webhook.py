import telebot
from flask import Flask, request

app = Flask(__name__)
BOT_TOKEN = "8266443596:AAE-ziq6rRzR0zZ1Ga5Ubgq2JO6M_eTjS2k"
bot = telebot.TeleBot(8266443596:AAE-ziq6rRzR0zZ1Ga5Ubgq2JO6M_eTjS2k

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def home():
    return "Paytm UPI subscription bot is running!"

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://now-1uxz.onrender.com/{8266443596:AAE-ziq6rRzR0zZ1Ga5Ubgq2JO6M_eTjS2k}")
    app.run(host='0.0.0.0', port=5000)

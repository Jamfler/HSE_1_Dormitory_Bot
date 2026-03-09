import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
VERIFICATION_PASSWORD = os.getenv("VERIFICATION_PASSWORD", "1234")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
DB_PATH = os.getenv("DB_PATH", "coworking.db")

# Настройки для Webhook (Render.com)
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST") # Например: https://my-bot.onrender.com
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))
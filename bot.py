import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from config import BOT_TOKEN, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_PATH
from database import init_db
from handlers import verify, booking # Импорт ваших роутеров
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiosqlite
from config import DB_PATH

logging.basicConfig(level=logging.INFO)

async def clean_old_bookings():
    """Фоновая задача очистки БД (старше 14 дней)"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM bookings WHERE date < date('now', '-14 days')")
        await db.commit()
    logging.info("Old bookings cleaned up.")

async def on_startup(bot: Bot):
    await init_db()
    await bot.set_webhook(WEBHOOK_URL)
    
    # Настройка планировщика очистки БД
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clean_old_bookings, 'cron', hour=3, minute=0)
    scheduler.start()

def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(verify.router)
    dp.include_router(booking.router)
    dp.startup.register(on_startup)

    # Настройка aiohttp для Webhook на Render.com
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    main()
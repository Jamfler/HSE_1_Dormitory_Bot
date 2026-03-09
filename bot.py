import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from config import BOT_TOKEN, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_PATH
from database import init_db
from handlers import verify, booking, view  # Не забудь добавить view, если создал его
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)

# --- НОВАЯ ФУНКЦИЯ ДЛЯ МЕНЮ ---
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='Запустить бота'),
        BotCommand(command='/view', description='Все брони'),
        BotCommand(command='/book', description='Забронировать'),
        BotCommand(command='/my', description='Мои брони'),
        BotCommand(command='/delete', description='Отменить бронь'),
        BotCommand(command='/verify', description='Верификация'),
        BotCommand(command='/rules', description='Правила')
    ]
    await bot.set_my_commands(main_menu_commands)

async def on_startup(bot: Bot):
    await init_db()           # Инициализация базы данных
    await set_main_menu(bot)  # РЕГИСТРАЦИЯ МЕНЮ
    await bot.set_webhook(WEBHOOK_URL)
    
    # Настройка планировщика очистки БД
    scheduler = AsyncIOScheduler()
    # Функция clean_old_bookings должна быть импортирована или определена
    # scheduler.add_job(clean_old_bookings, 'cron', hour=3, minute=0)
    scheduler.start()

def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(verify.router)
    dp.include_router(booking.router)
    if 'view' in globals():
        dp.include_router(view.router)
    
    dp.startup.register(on_startup)

    # Настройка aiohttp для Webhook на Render.com
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    main()

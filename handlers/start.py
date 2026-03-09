from aiogram import Router, types
from aiogram.filters import CommandStart
from database import get_user

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user = await get_user(message.from_user.id)
    
    if not user or not user['is_verified']:
        await message.answer(
            "👋 Привет! Это бот бронирования коворкинга.\n\n"
            "Чтобы начать пользоваться, тебе нужно пройти верификацию.\n"
            "Жми 👉 /verify"
        )
    else:
        await message.answer(
            f"С возвращением, {user['username']}! 👋\n\n"
            "📋 **Доступные команды:**\n\n"
            "📅 /book — Инструкция по бронированию\n"
            "📋 /view — Посмотреть все брони\n"
            "👤 /my — Мои бронирования\n"
            "❌ /delete — Отменить свою бронь\n"
            "📝 /rename — Изменить своё имя\n"
            "📍 /rules — Правила коворкинга\n"
            "🔘 /buttons — Кнопки быстрого доступа"
        )
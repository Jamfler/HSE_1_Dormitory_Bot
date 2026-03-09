from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import aiosqlite
from config import VERIFICATION_PASSWORD, DB_PATH
from datetime import datetime

router = Router()

class VerifyStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_name = State()

@router.message(Command("verify"))
async def cmd_verify(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите пароль для верификации:")
    await state.set_state(VerifyStates.waiting_for_password)

@router.message(VerifyStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    if message.text == VERIFICATION_PASSWORD:
        await message.answer("Пароль верный. Пожалуйста, введите ваше имя и фамилию:\n"
                             "Советую формат: Фамилия Имя (например, Иванов Алексей)")
        await state.set_state(VerifyStates.waiting_for_name)
    else:
        await message.answer("Неверный пароль. Попробуйте снова: /verify")
        await state.clear()

@router.message(VerifyStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    words = message.text.strip().split()
    if len(words) < 2 or not all(len(w) >= 2 and w.isalpha() for w in words):
        await message.answer("Пожалуйста, введите реальные Имя и Фамилию (минимум 2 слова).")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (user_id, username, tg_handle, is_verified, verified_at)
            VALUES (?, ?, ?, 1, ?)
        """, (message.from_user.id, message.text, message.from_user.username, datetime.now()))
        await db.commit()

    await message.answer("Верификация завершена! Теперь вы можете бронировать коворкинг. Инструкция: /book")
    await state.clear()
from aiogram import Router, types
from aiogram.filters import Command
import aiosqlite
from config import DB_PATH
from utils import slot_to_time

router = Router()

@router.message(Command("view"))
async def cmd_view(message: types.Message):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Показываем только будущие брони
        async with db.execute("""
            SELECT b.*, u.username, u.tg_handle 
            FROM bookings b 
            JOIN users u ON b.user_id = u.user_id 
            WHERE b.date >= date('now') 
            ORDER BY b.date, b.start_slot
        """) as cursor:
            rows = await cursor.fetchall()

    if not rows:
        await message.answer("📋 Пока нет активных бронирований.")
        return

    text = "📋 **Все брони коворкинга:**\n"
    current_date = None

    for row in rows:
        if row['date'] != current_date:
            current_date = row['date']
            text += f"\n📅 **{current_date}**\n"
        
        start = slot_to_time(row['start_slot'])
        end = slot_to_time(row['end_slot'] + 1)
        text += f"• {start}–{end}: {row['username']} (@{row['tg_handle']})\n"

    await message.answer(text, parse_mode="Markdown")
    @router.message(Command("my"))
async def cmd_my(message: types.Message):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM bookings 
            WHERE user_id = ? AND date >= date('now') 
            ORDER BY date, start_slot
        """, (message.from_user.id,)) as cursor:
            rows = await cursor.fetchall()

    if not rows:
        await message.answer("📅 У тебя пока нет предстоящих бронирований.")
        return

    text = "📅 **Твои бронирования:**\n\n"
    for row in rows:
        start = slot_to_time(row['start_slot'])
        end = slot_to_time(row['end_slot'] + 1)
        text += f"• {row['date']}: {start}–{end}\n"
    
    await message.answer(text)

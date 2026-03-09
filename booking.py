from aiogram import Router, F, types
from database import get_user
from utils import parse_booking_text, slot_to_time
from validators import validate_booking
import aiosqlite
from config import DB_PATH

router = Router()

@router.message(F.text & ~F.text.startswith("/"))
async def process_booking_text(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user or not user['is_verified']:
        return # Игнорируем текст от неверифицированных

    parsed = parse_booking_text(message.text)
    if not parsed:
        await message.answer("Не удалось распознать бронь. Используй /book для инструкции.")
        return

    is_valid, msg = await validate_booking(
        user_id=message.from_user.id,
        target_date=parsed['date'],
        start_slot=parsed['start_slot'],
        end_slot=parsed['end_slot']
    )

    if not is_valid:
        await message.answer(msg)
        return

    slots_count = parsed['end_slot'] - parsed['start_slot'] + 1
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO bookings (user_id, date, start_slot, end_slot, slots_count)
            VALUES (?, ?, ?, ?, ?)
        """, (message.from_user.id, parsed['date'], parsed['start_slot'], parsed['end_slot'], slots_count))
        await db.commit()

    start_time_str = slot_to_time(parsed['start_slot'])
    end_time_str = slot_to_time(parsed['end_slot'] + 1) # Показываем конец по времени

    await message.answer(f"✅ Готово! Забронировано:\n"
                         f"📅 {parsed['date'].strftime('%d.%m')} ({parsed['date'].strftime('%A')})\n"
                         f"⏰ {start_time_str} — {end_time_str} ({slots_count} слотов)\n"
                         f"👤 {user['username']}")
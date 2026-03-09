from datetime import datetime, date, timedelta
import aiosqlite
from config import DB_PATH

async def validate_booking(user_id: int, target_date: date, start_slot: int, end_slot: int) -> tuple[bool, str]:
    now = datetime.now()
    slots_count = end_slot - start_slot + 1
    
    # 1. Не позднее чем за 3 часа
    booking_dt = datetime.combine(target_date, datetime.min.time()) + timedelta(minutes=start_slot * 30)
    if booking_dt < now + timedelta(hours=3):
        return False, "❌ Бронирование возможно не позднее чем за 3 часа до начала."

    # 2. Не более чем за неделю
    if target_date > now.date() + timedelta(days=7):
        return False, "❌ Бронирование возможно не более чем за неделю вперёд."

    # 3. Не суббота
    if target_date.weekday() == 5:
        return False, "❌ Суббота — свободный день, бронирование запрещено."

    # 4. Минимум 2 слота
    if slots_count < 2:
        return False, "❌ Минимальная бронь — 1 час (2 слота)."

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Получаем брони пользователя на этот день
        async with db.execute("SELECT start_slot, end_slot, slots_count FROM bookings WHERE user_id = ? AND date = ?", (user_id, target_date)) as cursor:
            user_day_bookings = await cursor.fetchall()
            
        # 5. Максимум 7 слотов в день
        total_day_slots = sum(b['slots_count'] for b in user_day_bookings) + slots_count
        if total_day_slots > 7:
            return False, "❌ Превышен лимит 7 слотов (3,5 часа) в день."

        # 6. Нет разрыва в 1 слот
        for b in user_day_bookings:
            # Разрыв ровно в 1 слот до или после новой брони
            if start_slot - b['end_slot'] == 2 or b['start_slot'] - end_slot == 2:
                return False, "❌ Нельзя оставлять разрыв ровно в 1 слот (30 мин) между бронями."

        # 7. Два дня подряд
        yesterday = target_date - timedelta(days=1)
        tomorrow = target_date + timedelta(days=1)
        async with db.execute("SELECT COUNT(*) as c FROM bookings WHERE user_id = ? AND date IN (?, ?)", (user_id, yesterday, tomorrow)) as cursor:
            row = await cursor.fetchone()
            if row['c'] > 0:
                return False, "❌ Нельзя бронировать коворкинг два дня подряд."

        # 8. Не более 2 раз в неделю (пн-вс)
        start_of_week = target_date - timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        async with db.execute("SELECT COUNT(DISTINCT date) as c FROM bookings WHERE user_id = ? AND date >= ? AND date <= ?", (user_id, start_of_week, end_of_week)) as cursor:
            row = await cursor.fetchone()
            # Учитываем, если он бронирует на новый день на этой неделе
            is_new_day = all(b['date'] != target_date for b in user_day_bookings) if user_day_bookings else True
            if row['c'] >= 2 and is_new_day:
                return False, "❌ Превышен лимит: 2 дня бронирования в неделю."

        # 9. Пересечение с чужими бронями
        async with db.execute("""
            SELECT u.username FROM bookings b 
            JOIN users u ON b.user_id = u.user_id
            WHERE b.date = ? AND (? <= b.end_slot AND ? >= b.start_slot)
        """, (target_date, start_slot, end_slot)) as cursor:
            overlap = await cursor.fetchone()
            if overlap:
                return False, f"❌ Это время уже занято пользователем {overlap['username']}."

    return True, "✅ Успешно"
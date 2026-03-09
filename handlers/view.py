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

import re
from datetime import datetime, date, timedelta

def time_to_slot(time_str: str) -> int:
    """Переводит время '15:00' или '15.30' в номер слота (0-47)."""
    clean_time = time_str.replace('.', ':')
    hours, minutes = map(int, clean_time.split(':'))
    return hours * 2 + (1 if minutes >= 30 else 0)

def slot_to_time(slot: int) -> str:
    """Переводит номер слота (0-47) в строку '15:00'."""
    hours = slot // 2
    minutes = "30" if slot % 2 != 0 else "00"
    return f"{hours:02d}:{minutes}"

def parse_booking_text(text: str):
    """Парсит сообщение бронирования: [дата] [начало] [конец]"""
    pattern = r"(?:(\d{1,2}[\.\/]\d{1,2}|\d{1,2})\s+)?(\d{1,2}[:\.]\d{2}|\d{4})\s+(\d{1,2}[:\.]\d{2}|\d{4})"
    match = re.search(pattern, text)
    if not match:
        return None
    
    date_str, start_str, end_str = match.groups()
    
    # Обработка даты
    today = datetime.now().date()
    target_date = today
    if date_str:
        if '.' in date_str or '/' in date_str:
            day, month = map(int, re.split(r'[\.\/]', date_str))
            target_date = date(today.year, month, day)
            if target_date < today: # Если месяц прошел, значит следующий год
                target_date = target_date.replace(year=today.year + 1)
        else:
            day = int(date_str)
            target_date = target_date.replace(day=day)
            if target_date < today: # Если день прошел, значит следующий месяц
                month = today.month + 1 if today.month < 12 else 1
                year = today.year if today.month < 12 else today.year + 1
                target_date = target_date.replace(year=year, month=month)

    start_slot = time_to_slot(start_str)
    # Если бронь до 17:30, то последний занятый слот — 17:00 (slot - 1)
    end_slot = time_to_slot(end_str) - 1 

    if end_slot < start_slot:
        return None

    return {"date": target_date, "start_slot": start_slot, "end_slot": end_slot}
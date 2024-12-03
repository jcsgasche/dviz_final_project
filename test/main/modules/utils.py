# modules/utils.py
from datetime import datetime, timedelta

def calculate_date_range():
    today = datetime.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)
    return first_day_last_month, last_day_last_month
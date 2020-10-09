import pytz
from datetime import datetime

tz_moscow = pytz.timezone('Europe/Moscow')

def what_time(shift=0):
	d = datetime.now(tz_moscow)
	hour = d.strftime("%H")
	minute = str(shift + d.minute)
	if hour == minute[::-1]:
		if hour == "06": # Исключение невозможного 06:60
			return False
		else:
			return (f"{hour}:{minute}")
	elif hour == "23" and minute == "60": # Исключение 00:00
		return "00:00"
	else:
		return False
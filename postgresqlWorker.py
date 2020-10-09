import os
import psycopg2
import pytz
from datetime import datetime


DATABASE_URL = os.environ['DATABASE_URL']

tz_moscow = pytz.timezone('Europe/Moscow')

class DataBasePSQL:

	def __init__(self):
		"""Подключаемся к БД"""
		self.connection = conn = psycopg2.connect(DATABASE_URL, sslmode='require')

	def add_subscription(self, user_id, subscription=True, subscription1min=False, notification=True):
		"""Добавляем нового подписчика"""
		with self.connection.cursor() as cur:
			current_time = datetime.now(tz_moscow)
			cur.execute(f"INSERT INTO databasebot (telegram_id, datetime_change, subscribe_in_time, subscribe_1_min, notifications) VALUES ({user_id}, '{current_time}', {subscription}, {subscription1min}, {notification});")
			self.connection.commit()

	def update_subscription(self, user_id, subscription=False, subscription1min=False):
		"""Изменяем подписку (по умолчанию отписываемся от всего)"""
		with self.connection.cursor() as cur:
			current_time = datetime.now(tz_moscow)
			cur.execute(f"UPDATE databasebot SET datetime_change = '{current_time}', subscribe_in_time = {subscription}, subscribe_1_min = {subscription1min} WHERE telegram_id = {user_id};")
			self.connection.commit()

	def update_notification(self, user_id, notification=True):
		"""Обновляем наличие звуковых уведомлений"""
		with self.connection.cursor() as cur:
			current_time = datetime.now(tz_moscow)
			cur.execute(f"UPDATE databasebot SET datetime_change = '{current_time}', notifications = {notification} WHERE telegram_id = {user_id};")
			self.connection.commit()

	def get_subscriptions(self, subscription=True):
		"""Получаем подписчиков с уровнем пописки 'в момент'"""
		with self.connection.cursor() as cur:
			cur.execute(f"SELECT * FROM databasebot WHERE subscribe_in_time = {subscription};")
			return cur.fetchall()

	def get_subscriptions1min(self, subscription1min=True):
		"""Получаем подписчиков с уровнем пописки 'за минуту'"""
		with self.connection.cursor() as cur:
			cur.execute(f"SELECT * FROM databasebot WHERE subscribe_1_min = {subscription1min};")
			return cur.fetchall()

	def subscriber_exists(self, user_id):
		"""Проверяем, новый ли пользователь"""
		with self.connection.cursor() as cur:
			cur.execute(f"SELECT * FROM databasebot WHERE telegram_id = {user_id};")
			check = cur.fetchall()
			return bool(len(check))
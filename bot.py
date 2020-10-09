from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
import asyncio
import logging

from postgresqlWorker import DataBasePSQL
from config import API_TOKEN
import utils

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
db = DataBasePSQL()

# Кнопки и клавиатуры меню
button_sub = KeyboardButton('Подписаться!')
button_delivery = KeyboardButton('Настроить момент отправки уведомлений')
button_notification = KeyboardButton('Настроить наличие звуковых уведомлений')
button_back = KeyboardButton('Назад')
button_time_1min = KeyboardButton('Отправлять сообщения за одну минуту')
button_time = KeyboardButton('Отправлять сообщения в момент наступления')
button_notif_false = KeyboardButton('Будь тихим')
button_notif_true = KeyboardButton('Звини как можешь!')
button_settings = KeyboardButton('Настройки')
key_board1 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_sub)
key_board2 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_delivery).add(button_notification).add(button_back)
key_board3 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_time_1min).add(button_time)
key_board4 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_notif_false).add(button_notif_true)
key_board5 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_settings)

# Отработка команд
@dp.message_handler(commands=['start','help'])
async def process_start_command(message: types.Message):
	await message.answer("Если ты получаешь эстетичсекое удовольствие от идеальных вещей\
		или просто не хочешь лишний раз упускать возможномть загадать желание, то Я это то, что тебе нужно!)\
		\nПодпишись на отправку уведомлений о приближающемся или наступившем симметричном времени!", reply_markup=key_board1)

# Отработка нажатий кнопок в меню
@dp.message_handler()
async def process_menu(message: types.Message):
	if message.text == 'Подписаться!': 
		if(not db.subscriber_exists(message.from_user.id)):
			# если пользователя нет в базе, добавляем его
			db.add_subscription(message.from_user.id)
		else:
			# если он уже есть, то обновляем ему статус подписки
			db.update_subscription(message.from_user.id, subscription=True, subscription1min=False)
	
		await message.answer("Готово! Теперь меня можно немного настроить", reply_markup=key_board2)

	if message.text == 'Настроить момент отправки уведомлений':
		await message.answer("Я могу отправлять уведомления за одну минуту или в момент наступления заветного времени. Выбирай!", reply_markup=key_board3)

	if message.text == 'Отправлять сообщения за одну минуту':
		db.update_subscription(message.from_user.id, subscription=False, subscription1min=True)
		await message.answer("Теперь сообщения будут приходить за минуту!", reply_markup=key_board2)

	if message.text == 'Отправлять сообщения в момент наступления':
		db.update_subscription(message.from_user.id, subscription=True, subscription1min=False)
		await message.answer("Теперь сообщения будут приходить, когда на часах пробьет нужное время!", reply_markup=key_board2)

	if message.text == 'Настроить наличие звуковых уведомлений':
		await message.answer("Я могу отправлять уведомления со звуком или без, чтобы лишний раз тебя не отвлекать. Выбор за тобой!", reply_markup=key_board4)

	if message.text == 'Будь тихим':
		db.update_notification(message.from_user.id, notification=False)
		await message.answer("Буду нем как рыба", reply_markup=key_board2)

	if message.text == 'Звини как можешь!':
		db.update_notification(message.from_user.id, notification=True)
		await message.answer("Договорились!", reply_markup=key_board2)

	if message.text == 'Настройки':
		await message.answer("Настрой меня как тебе вздумается", reply_markup=key_board2)

	if message.text == 'Назад':
		await message.answer("Осталось дождаться нужного времени и я напишу тебе!", reply_markup=key_board5)

# Отработка задания. Каждые 10 секунд проверяем время
async def scheduled(wait_for):
	while True:
		suitable_time = utils.what_time(shift=1)
		if suitable_time:
			subscriptions = db.get_subscriptions1min()
			for s in subscriptions:
				await bot.send_message(s[1], f"Через минуту на часах определенно будет симметричное время {suitable_time}!", disable_notification=s[5])
			await asyncio.sleep(61)
			subscriptions = db.get_subscriptions()
			for s in subscriptions:
				await bot.send_message(s[1], utils.what_time() + " на часах!", disable_notification=s[5])
		await asyncio.sleep(wait_for)
	
if __name__ == '__main__':
	# Постановка заданий. Ожидание команд от пользователя и сопрограмма проверки времени
	ioloop = asyncio.get_event_loop()
	tasks = [
		ioloop.create_task(scheduled(10)),
		ioloop.create_task(executor.start_polling(dp, skip_updates=True)),
	]
	ioloop.run_until_complete(tasks)
	ioloop.close()
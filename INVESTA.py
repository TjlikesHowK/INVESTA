from currency_converter import CurrencyConverter as cc
import perk_scrap as ps
import asyncio
import emoji

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

btn_add = KeyboardButton(emoji.emojize(":check_mark_button:") + " Купить")
btn_del = KeyboardButton(emoji.emojize(":cross_mark:") + " Продать")
btn_cur = KeyboardButton(emoji.emojize(":currency_exchange:") + " Валюта")
btn_sta = KeyboardButton(emoji.emojize(":money_bag:") + " Профит")
btn_ptf = KeyboardButton(emoji.emojize(":briefcase:") + " Портфель")

btn_stop = KeyboardButton("Стоп")

btn_rub = InlineKeyboardButton(text = "RUB", callback_data = "rub")
btn_usd = InlineKeyboardButton(text = "USD", callback_data = "usd")

btn_brf = InlineKeyboardButton(text = "Кратко", callback_data = "briefly")
btn_exp = InlineKeyboardButton(text = "Развёрнуто", callback_data = "expanded")

cur_kb = InlineKeyboardMarkup(resize_keyboard = True).add(
	btn_rub).add(
	btn_usd)

main_kb = ReplyKeyboardMarkup(resize_keyboard = True).row(
	btn_add, btn_del).row(
	btn_sta, btn_cur).add(
	btn_ptf)

sta_kb = InlineKeyboardMarkup(resize_keyboard = True).add(
	btn_exp).add(
	btn_brf)

stop_kb = ReplyKeyboardMarkup(resize_keyboard = True).add(
	btn_stop)

token = "2034540352:AAHBga23bcTZdfrHypyCl-g9g4zk77fn7Vk"

curChanger = {
	"HHR": "USD",
	"MBT": "USD",
	"OZON": "RUB",
	"QIWI": "RUB",
	"YNDX": "RUB"}

add_t = [
	emoji.emojize(":check_mark_button:") + " Купить",
	"Купить",
	"/add"]

del_t = [
	emoji.emojize(":cross_mark:") + " Продать",
	"Продать",
	"/del"]

cur_t = [
	emoji.emojize(":currency_exchange:") + " Валюта",
	"Валюта",
	"/cur"]

sta_t = [
	emoji.emojize(":money_bag:") + " Профит",
	"Профит",
	"/sta"]

ptf_t = [
	emoji.emojize(":briefcase:") + " Портфель",
	"Портфель",
	"/ptf"]

stop_t = [
	"Стоп",
	"/stop"]

Log = set()
Users = set()
loop = asyncio.get_event_loop()
bot = Bot(token = token)
dp = Dispatcher(bot, loop = loop)
c = cc();

with open("Users.txt", "r", encoding = "utf-8") as f:
	for line in f:
		line = line.strip()
		user_id, currency = line.split()

		log = [user_id, currency, "none"]

		if not(str(user_id) in Users):
			Users.add(log[0])
			Log.add(str(log))

async def adding(user_id, item):
	try:
		tick, e_price, qntty = item.split()

		e_price = float(e_price.replace(",", "."))
		qntty = float(qntty)

		txt = ""
		old_user = False

		with open("ticks.txt", "r") as f:
			for line in f:
				if str(user_id) in line and tick in line:
					var_id, var_tick, var_price, var_qntty = line.split()

					txt += f"{var_id} {var_tick} {round(float(var_price) + e_price, 2) / 2} {round(float(var_qntty) + qntty, 2)}\n"

					old_user = True

					del var_id, var_tick, var_price, var_qntty

				else:
					txt += line

		if(old_user):
			with open("ticks.txt", "w") as f:
				f.write(txt)
		else:
			with open("ticks.txt", "a") as f:
				f.write(f"{user_id} {tick} {e_price} {qntty}\n")

		del txt, tick, e_price, qntty, old_user

	except Exception as err:
			print(f"{user_id} caused an error in [/add] (adding): {err}")

			await bot.send_message(user_id, text =
				"Произошла ошибка. Пожалуйста, повторите запрос позже.", reply_markup = main_kb)

async def deleting(user_id, item):
	try:
		tick, qntty = item.split()

		qntty = float(qntty)
		old_user = False
		txt = ""

		with open("ticks.txt", "r") as f:
			for line in f:
				if str(user_id) in line and tick in line:
					var_id, var_tick, var_price, var_qntty = line.split()

					if(float(var_qntty) - qntty <= 0):
						txt += ""
					else:
						txt += f"{var_id} {var_tick} {var_price} {round(float(var_qntty) - qntty, 2)}\n"

					old_user = True

					del var_id, var_tick, var_price, var_qntty

				else:
					txt += line

		if(old_user):
			with open("ticks.txt", "w") as f:
				f.write(txt)

		del txt, tick, qntty, old_user

	except Exception as err:
			print(f"{user_id} caused an error in [/del] (deleting): {err}")

			await bot.send_message(user_id, text =
				"Произошла ошибка. Пожалуйста, повторите запрос позже.", reply_markup = main_kb)

async def USDRUB(user_id, cur):
	global Users, Log

	txt = ""
	past_cur = "RUB"

	if(cur == "RUB"):
		past_cur = "USD"

	with open("Users.txt", "r") as f:
		for line in f:
			if(f"{user_id} {past_cur}" in line):
				txt += f"{user_id} {cur}\n"

				log = [str(user_id), {cur}, "none"]
				Log.remove(f"['{user_id}', '{past_cur}', 'none']")
				Log.add(str(log))

			else:
				txt += line

	with open("Users.txt", "w") as f:
		f.write(txt)

	del txt, past_cur

async def profitAcc(portfolio, line, chosen_cur):
	user_id, stock, user_price, qntty = line.split()
	live_price, change_per_day, stock_cur = ps.driver(stock)

	edit_user_price = user_price
	edit_live_price = live_price

	if stock_cur != chosen_cur or stock in curChanger:
		user_price = round(c.convert(user_price, stock_cur, chosen_cur), 2)

		if stock in curChanger:
			live_price = round(c.convert(live_price, stock_cur, curChanger[stock]), 2)

			edit_user_price = user_price
			edit_live_price = live_price

		else: 
			live_price = round(c.convert(live_price, stock_cur, chosen_cur), 2)

	if stock in curChanger:
		live_price = round(c.convert(live_price, curChanger[stock], chosen_cur), 2)
		user_price = round(c.convert(user_price, curChanger[stock], chosen_cur), 2)

		portfolio += round(round(float(live_price) - float(user_price), 2) * float(qntty), 2)

	else:
		portfolio += round(round(float(live_price) - float(user_price), 2) * float(qntty), 2)

	d1 = round(float(edit_live_price) - float(edit_user_price), 2)
	d2 = round(((float(edit_live_price) * 100) / float(edit_user_price)) - 100, 2)

	change_per_time = f"{d1}({d2}%)".replace("e-", "+").replace("-", "−").replace("+", "e-")

	del user_id, user_price, stock_cur, live_price

	return change_per_day, change_per_time, stock, qntty, edit_user_price, edit_live_price

@dp.message_handler(commands = ['start', 'call', 'info'])
async def start_command(msg: types.Message):
	global Users, Log

	user_id = msg.from_user.id

	print(f"{user_id} used /start")

	if not(str(user_id) in Users):
		with open("Users.txt", "a") as f:
			log = [str(user_id), "RUB", "none"]
			f.write(f"{log[0]} {log[1]}\n")
			Users.add(log[0])
			Log.add(str(log))

	await msg.reply( 
		"Этот бот создан для анализа вашего инвестиционного портфеля. Вы можете добавить сюда информацию о своих акциях/криптовалюте, и наблюдать за своим прогрессом.\n\n" + 
		"Существующие команды:\n\n" +
		emoji.emojize(":check_mark_button:") + " Для покупки акции в портфель используйте кнопку «Купить». Вводите акции в формате ТИКЕР ЦЕНА ПОКУПКИ КОЛИЧЕСТВО (например, TSLA 700 10)\n\n" +
		emoji.emojize(":cross_mark:") + " Для продажи акции из портфеля - кнопка «Продать». Вводите параметры акций в формате ТИКЕР КОЛИЧЕСТВО (например, TSLA 10)\n\n" +
		emoji.emojize(":briefcase:") + " Для просмотра текущей портфеля - кнопка «Портфель»\n\n" +
		emoji.emojize(":money_bag:") + " Для просмотра динамики (прибыли или убытка) - кнопка «Профит»\n\n" +
		emoji.emojize(":currency_exchange:") + " Для смены валюты используйте кнопку «Валюта».", 
		reply_markup = main_kb)

@dp.message_handler()
async def start_command(msg: types.Message):
	global Users, Log

	add_ = False
	del_ = False

	user_id = msg.from_user.id

	for user in Log:
		if(str(user_id) in user):
			if("add" in user):
				add_ = True
			elif("del" in user):
				del_ = True
			else:
				add_ = False
				del_ = False

			break

	if(msg.text in stop_t):
		await bot.send_message(user_id, text = "Работа с акциями завершена", reply_markup = main_kb)

		chosen_cur = "RUB"

		for user in Log:
			if(str(user_id) in user):
				if("USD" in user):
					chosen_cur = "USD"
				if("add" in user):
					Log.remove(f"['{user_id}', '{chosen_cur}', 'add']")
				else:
					Log.remove(f"['{user_id}', '{chosen_cur}', 'del']")

				break

		log = [str(user_id), str(chosen_cur), "none"]
		Log.add(str(log))

	elif(add_):
		if "\n" in msg.text:
			drop = msg.text.split('\n')

			for item in drop:
				print(item)
				await adding(user_id, item)

			del drop

			await msg.reply(text = "Акции были успешно сохранены!", reply_markup = stop_kb)
		else:
			await adding(user_id, msg.text)

			await msg.reply(text = "Акция была успешно сохранена!", reply_markup = stop_kb)

	elif(del_):
		if "\n" in msg.text:
			drop = msg.text.split('\n')

			for item in drop:
				await deleting(user_id, item)

			del drop

			await bot.send_message(user_id, text = "Акции были успешно удалены!", reply_markup = stop_kb)
		else:
			await deleting(user_id, msg.text)

			await bot.send_message(user_id, text = "Акция была успешно удалена!", reply_markup = stop_kb)

	elif(msg.text in add_t) and (not(add_) or not(del_)):
		print(f"{user_id} used /add")

		await bot.send_message(user_id, text = 
			"Ввод - <Тикер> <Цена> <Кол-во>\n" +
			"Пример - TSLA 700 10", reply_markup = stop_kb)

		chosen_cur = "RUB"

		for user in Log:
			if(str(user_id) in user):
				if("USD" in user):
					chosen_cur = "USD"

				break

		log = [str(user_id), str(chosen_cur), "add"]
		Log.remove(f"['{user_id}', '{chosen_cur}', 'none']")
		Log.add(str(log))

	elif(msg.text in del_t) and (not(add_) or not(del_)):
		print(f"{user_id} used /del")

		await bot.send_message(user_id, text = 
			"Ввод - <Тикер> <Кол-во>\n" +
			"Пример - TSLA 10", reply_markup = stop_kb)

		chosen_cur = "RUB"

		for user in Log:
			if(str(user_id) in user):
				if("USD" in user):
					chosen_cur = "USD"

				break

		log = [str(user_id), str(chosen_cur), "del"]
		Log.remove(f"['{user_id}', '{chosen_cur}', 'none']")
		Log.add(str(log))

	elif(msg.text in cur_t) and (not(add_) or not(del_)):
		print(f"{user_id} used /cur")

		await msg.reply("Выберите валюту", reply_markup = cur_kb)

	elif(msg.text in sta_t) and (not(add_) or not(del_)):
		print(f"{user_id} used /sta")

		await msg.reply("Выберите вид сообщения", reply_markup = sta_kb)

	elif(msg.text in ptf_t) and (not(add_) or not(del_)):
		print(f"{user_id} used /ptf")

		try:
			text = ""

			with open("ticks.txt", "r") as f:
				for line in f:
					if(str(user_id) in str(line)):
						txt_user_id, stock, price, qntty = str(line).split()

						text += f"{stock}  :  {price} | {qntty}\n" + "-"*10 + "\n"

			if text == "":
				await bot.send_message(user_id, text = "Портфель пуст", reply_markup = main_kb)
			else:
				await bot.send_message(user_id, text = text, reply_markup = main_kb)

			del text

		except Exception as err:
			print(f"{msg.from_user.id} caused an error in [/sta]: {err}")

			await bot.send_message(msg.from_user.id, text =
				"Произошла ошибка. Пожалуйста, повторите запрос позже.", reply_markup = main_kb)

@dp.callback_query_handler(lambda c: c.data)
async def cur_callback(callback_query: types.CallbackQuery):
	global Users, Log

	user_id = str(callback_query.from_user.id)

	if(callback_query.data == "rub"):
		print(f"{user_id} used [/cur] - rub")

		try:
			await USDRUB(user_id, "RUB")

			await bot.answer_callback_query(callback_query.id, "Ваша расчётная валюта была успешно изменена на RUB")
			await bot.send_message(user_id, "Ваша расчётная валюта была успешно изменена на RUB")

		except Exception as err:
			print(f"{user_id} caused an error in [/rub]: {err}")

			await bot.send_message(user_id,
				"Произошла ошибка. Пожалуйста, повторите запрос позже.")

	elif(callback_query.data == "usd"):
		print(f"{user_id} used [/cur] - usd")

		try:
			await USDRUB(user_id, "USD")

			await bot.answer_callback_query(callback_query.id, "Ваша расчётная валюта была успешно изменена на USD")
			await bot.send_message(user_id, "Ваша расчётная валюта была успешно изменена на USD")

		except Exception as err:
			print(f"{user_id} caused an error in [/usd]: {err}")

			await bot.send_message(user_id,
				"Произошла ошибка. Пожалуйста, повторите запрос позже.")

	elif(callback_query.data == "briefly"):
		print(f"{user_id} used [/profit] - briefly")

		try:
			portfolio = 0

			await bot.send_message(user_id,
				emoji.emojize(":hourglass_done:") + " Пожалуйста, подождите...")

			with open("ticks.txt", "r") as f:
				briefly_text = "+/- | ticker | qntty | entry | current\n\n"

				chosen_cur = "RUB"

				for user in Log:
					if(user_id in user):
						if("USD" in user):
							chosen_cur = "USD"

						break

				for line in f:
					if(user_id in line):
						change_per_day, change_per_time, stock, qntty, edit_user_price, edit_live_price = await profitAcc(portfolio, line, chosen_cur)

						if("−" in str(change_per_day)):
							if("−" in str(change_per_time)):
								briefly_text += emoji.emojize(":red_circle:") + f"  {stock}  {qntty}  {edit_user_price}  {edit_live_price}  \n" + emoji.emojize(":down_arrow: ") + f"{change_per_day} — change per day\n" + emoji.emojize(":down_arrow: ") + f"{change_per_time} — change per time\n\n"
							
							else:
								briefly_text += emoji.emojize(":green_circle:") + f"  {stock}  {qntty}  {edit_user_price}  {edit_live_price}  \n" + emoji.emojize(":down_arrow: ") + f"{change_per_day} — change per day\n" + emoji.emojize(":up_arrow: ") + f"{change_per_time} — change per time\n\n"
						else:
							if("−" in str(change_per_time)):
								briefly_text += emoji.emojize(":red_circle:") + f"  {stock}  {qntty}  {edit_user_price}  {edit_live_price}  \n" + emoji.emojize(":up_arrow: ") + f"{change_per_day} — change per day\n" + emoji.emojize(":down_arrow: ") + f"{change_per_time} — change per time\n\n"
							
							else:
								briefly_text += emoji.emojize(":green_circle:") + f"  {stock}  {qntty}  {edit_user_price}  {edit_live_price}  \n" + emoji.emojize(":up_arrow: ") + f"{change_per_day} — change per day\n" + emoji.emojize(":up_arrow: ") + f"{change_per_time} — change per time\n\n"

				await bot.send_message(user_id,
					briefly_text +
					"========================\n" +
					emoji.emojize(":money_bag:") + f" Выигрыш: {round(portfolio, 2)} ({chosen_cur})")

			del portfolio 

		except Exception as err:
			print(f"{user_id} caused an error in [/profit]: {err}")

			await bot.send_message(user_id,
				"Произошла ошибка. Пожалуйста, повторите запрос позже.")

	elif(callback_query.data == "expanded"):
		print(f"{user_id} used [/profit] - expanded")

		try:
			portfolio = 0

			await bot.send_message(user_id,
				emoji.emojize(":hourglass_done:") + " Пожалуйста, подождите...")

			with open("ticks.txt", "r") as f:
				expanded_text = ""
				chosen_cur = "RUB"

				for user in Log:
					if(user_id in user):
						if("USD" in user):
							chosen_cur = "USD"

						break

				for line in f:
					if(user_id in line):
						change_per_day, change_per_time, stock, qntty, edit_user_price, edit_live_price = await profitAcc(portfolio, line, chosen_cur)

						if("−" in str(change_per_day)):
							if("−" in str(change_per_time)):
								expanded_text += emoji.emojize(":red_circle:") + f"   {stock}\nquantity: {qntty}\nentry price: {float(edit_user_price)}\ncurrent price: {float(edit_live_price)}\nprice change per day: " + emoji.emojize(":down_arrow: ") + f"{change_per_day}\nprice change per time: " + emoji.emojize(":down_arrow: ") + f"{change_per_time}\n\n"
							
							else:
								expanded_text += emoji.emojize(":green_circle:") + f"   {stock}\nquantity: {qntty}\nentry price: {float(edit_user_price)}\ncurrent price: {float(edit_live_price)}\nprice change per day: " + emoji.emojize(":down_arrow: ") + f"{change_per_day}\nprice change per time: " + emoji.emojize(":up_arrow: ") + f"{change_per_time}\n\n"
						else:
							if("−" in str(change_per_time)):
								expanded_text += emoji.emojize(":red_circle:") + f"   {stock}\nquantity: {qntty}\nentry price: {float(edit_user_price)}\ncurrent price: {float(edit_live_price)}\nprice change per day: " + emoji.emojize(":up_arrow: ") + f"{change_per_day}\nprice change per time: " + emoji.emojize(":down_arrow: ") + f"{change_per_time}\n\n"
							
							else:
								expanded_text += emoji.emojize(":green_circle:") + f"   {stock}\nquantity: {qntty}\nentry price: {float(edit_user_price)}\ncurrent price: {float(edit_live_price)}\nprice change per day: " + emoji.emojize(":up_arrow: ") + f"{change_per_day}\nprice change per time: " + emoji.emojize(":up_arrow: ") + f"{change_per_time}\n\n"

				await bot.send_message(user_id,
					expanded_text +
					"========================\n" +
					emoji.emojize(":money_bag:") + f" Выигрыш: {round(portfolio, 2)} ({chosen_cur})")

			del portfolio 

		except Exception as err:
			print(f"{user_id} caused an error in [/profit]: {err}")

			await bot.send_message(user_id,
				"Произошла ошибка. Пожалуйста, повторите запрос позже.")

if __name__ == '__main__':
	while True:		
		try:
			print("\nSuccessfully working....")

			executor.start_polling(dp, loop = loop)
		except Exception as err:
			print(f"Total error... \n\n{err}\n\nReloading...")

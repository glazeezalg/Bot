import re
import telebot
import Parse
import Table
from datetime import date

dataStart = date(year=2022, month=10, day=10)
bot = telebot.TeleBot("5700943159:AAF7cyKx3RZ7lk57PulnN9e1coMmfza2TcI")
university_data = []
save_university = ""
group_data = {}
nums_week = []
tables = []
url_timetable = ""

def cut_matrix(matrix, num):
    mat = []

    for i in range(len(matrix)):
        mat.append([matrix[i][0], matrix[i][num]])

    return mat

@bot.message_handler(commands=["start"])
def start(message):
    global university_data
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    university_data = Parse.parse_university()
    for t in university_data:
        markup.add(telebot.types.KeyboardButton(t))
    bot.send_message(chat_id=message.chat.id, text="<b>Здравствуйте! Выберите свой институт.</b>", reply_markup=markup, parse_mode="html")

@bot.message_handler(content_types=["text"])
def message(message):
    global university_data
    global save_university
    global group_data
    global nums_week
    global tables
    global url_timetable

    message_norm = message.text

    if message_norm == "К выбору института":
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        university_data = Parse.parse_university()
        for t in university_data:
            markup.add(telebot.types.KeyboardButton(t))
        bot.send_message(chat_id=message.chat.id, text="<b>Выберите свой институт.</b>", reply_markup=markup, parse_mode="html")
    
    if message_norm in university_data:
        save_university = message_norm
        group_data = Parse.parse_group(re.search(r"[(]\D*[)]", message_norm)[0])
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for t in group_data.keys():
            markup.add(telebot.types.KeyboardButton(t))
        markup.add(telebot.types.KeyboardButton("К выбору института"))
        bot.send_message(chat_id=message.chat.id, text="<b>Теперь выберите свою группу.</b>", reply_markup=markup, parse_mode="html")

    if not save_university: return start(message)

    if message_norm == "К выбору группы":
        group_data = Parse.parse_group(re.search(r"[(]\D*[)]", save_university)[0])
        markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        for t in group_data.keys():
            markup.add(telebot.types.KeyboardButton(t))
        markup.add(telebot.types.KeyboardButton("К выбору института"))
        bot.send_message(chat_id=message.chat.id, text="<b>Выберите свою группу.</b>", reply_markup=markup, parse_mode="html")
        
    if message_norm in group_data:
        tables, url_timetable = Parse.parse_timetable(group_data.get(message_norm))
        if (len(tables) > 1):
            nums_week = []
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            for t in range(len(tables)):
                nums_week.append(str(t + 1) + " неделя")
                markup.add(telebot.types.KeyboardButton(str(t + 1) + " неделя"))
            markup.add(telebot.types.KeyboardButton("Расписание на завтра"))
            markup.add(telebot.types.KeyboardButton("Расписание на сегодня"))
            markup.add(telebot.types.KeyboardButton("К выбору института"))
            markup.add(telebot.types.KeyboardButton("К выбору группы"))
            bot.send_message(chat_id=message.chat.id, text="<b>Выберите неделю.</b>", reply_markup=markup, parse_mode="html")
        else:
            if (len(tables) >= 1):
                matrix = Parse.set_table(tables[0])
                Table.create_table(matrix)
                bot.send_photo(message.chat.id, photo=open("table.png", "rb"))
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton("Нажмите, чтобы перейти на сайт с расписанием", url=url_timetable))
                bot.send_message(chat_id=message.chat.id, text="<b>Для вашего удобства я сгенерировал ссылку на расписание</b>", reply_markup=markup, parse_mode="html")
            else :
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton("Нажмите, чтобы перейти на сайт с расписанием", url=url_timetable))
                bot.send_message(chat_id=message.chat.id, text="<b>Я не могу понять это замудренное распиание, оставлю лучше вам ссылку.</b>", reply_markup=markup, parse_mode="html")
    
    if not save_university: return start(message)
    if not group_data: return start(message)

    if message_norm in nums_week:
        message_norm = message_norm.split(" ")[0]
        matrix = Parse.set_table(tables[int(message_norm) - 1])
        Table.create_table(matrix)
        bot.send_photo(message.chat.id, photo=open("table.png", "rb"))
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Нажмите, чтобы перейти на сайт с расписанием", url=url_timetable))
        bot.send_message(chat_id=message.chat.id, text="<b>Для вашего удобства я сгенерировал ссылку на расписание</b>", reply_markup=markup, parse_mode="html")

    if message_norm == "Расписание на завтра":
        dataNow = date.today()
        if ((dataNow - dataStart).days % 7 + 1> len(tables[(dataNow - dataStart).days // 7 % 2]) - 1):
            bot.send_message(chat_id=message.chat.id,
                             text="<b>У вас завтра выходной.</b>",
                             parse_mode="html")
        else:
            matrix = Parse.set_table(tables[(dataNow - dataStart).days // 7 % 2])
            matrix = cut_matrix(matrix, (dataNow - dataStart).days % 7 + 2)
            Table.create_table(matrix)
            bot.send_photo(message.chat.id, photo=open("table.png", "rb"))
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("Нажмите, чтобы перейти на сайт с расписанием", url=url_timetable))
            bot.send_message(chat_id=message.chat.id,
                             text="<b>Для вашего удобства я сгенерировал ссылку на расписание</b>", reply_markup=markup,
                             parse_mode="html")

    if message_norm == "Расписание на сегодня":
        dataNow = date.today()
        if ((dataNow - dataStart).days % 7 > len(tables[(dataNow - dataStart).days // 7 % 2]) - 1):
            bot.send_message(chat_id=message.chat.id,
                             text="<b>У вас сегодня выходной.</b>",
                             parse_mode="html")
        else:
            matrix = Parse.set_table(tables[(dataNow - dataStart).days // 7 % 2])
            matrix = cut_matrix(matrix, (dataNow - dataStart).days % 7 + 1)
            Table.create_table(matrix)
            bot.send_photo(message.chat.id, photo=open("table.png", "rb"))
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("Нажмите, чтобы перейти на сайт с расписанием", url=url_timetable))
            bot.send_message(chat_id=message.chat.id,
                             text="<b>Для вашего удобства я сгенерировал ссылку на расписание</b>", reply_markup=markup,
                             parse_mode="html")
print("BOT STARTED")
bot.polling(none_stop=True)

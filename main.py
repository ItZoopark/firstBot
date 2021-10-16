import os
import telebot
from flask import Flask, request
import json
import requests
from telebot import types

TOKEN = "2003680813:AAHB85TfLFidKVKHZFPEaJQsxa2Nzp_we8Y"

APP_URL = f"https://test-itdop-bot2021.herokuapp.com/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

typeNum = ''


@bot.message_handler(commands=['start'])
def start(message):
    try:
        # pic = open('welcome.jpeg', 'rb')
        pic = open('welcome.tgs', 'rb')
        bot.send_sticker(message.chat.id, pic)
        bot.send_message(message.from_user.id, "✋ Добро пожаловать!")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Викторина')
        item2 = types.KeyboardButton('Числа')
        markup.add(item1, item2)
        bot.send_message(message.chat.id, f'Привет! <b> {message.from_user.id} </b>'
                         , parse_mode='html', reply_markup=markup)
    except Exception as ex:
        print(ex)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    global typeNum
    if message.chat.type == 'private':
        if message.text == 'Викторина':
            while True:
                try:
                    response = requests.get('https://jservice.io/api/random?count=1')
                    json_str = str(response.json()).replace("\"", "_").replace("\'", "\"").replace("_", "\'").replace(
                        'None', 'null')
                    print(json_str)
                    json_res = json.loads(json_str)
                    print("question: " + json_res[0]['question'])
                    print("answer: " + json_res[0]['answer'])
                    # json_res = json.loads(json_dump)
                    bot.send_message(message.from_user.id, json_res[0]['question'])
                    break
                except Exception as ex:
                    print(ex)
        elif message.text == 'Числа':
            bot.send_message(message.from_user.id, "Выберите раздел")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Математика')
            item2 = types.KeyboardButton('Год')
            item3 = types.KeyboardButton('Дата')
            item4 = types.KeyboardButton('Факт')
            back = types.KeyboardButton('◀️ Назад')
            markup.add(item1, item2, item3, item4, back)
            bot.send_message(message.chat.id, 'Числа', reply_markup=markup)
        elif message.text == 'Математика':
            typeNum = 'math'
            bot.send_message(message.from_user.id, "Напишите число, про которое хотите узнать...")
            bot.register_next_step_handler(message, getNumberInfo)
            getNumberInfo(message)
        elif message.text == 'Год':
            typeNum = 'year'
            bot.send_message(message.from_user.id, "Напишите число, про которое хотите узнать...")
            bot.register_next_step_handler(message, getNumberInfo)
            getNumberInfo(message)
        elif message.text == 'Дата':
            typeNum = 'date'
            bot.send_message(message.from_user.id, "Напишите число, про которое хотите узнать...")
            bot.register_next_step_handler(message, getNumberInfo)
            getNumberInfo(message)
        elif message.text == 'Факт':
            typeNum = 'trivia'
            bot.send_message(message.from_user.id, "Напишите число, про которое хотите узнать...")
            bot.register_next_step_handler(message, getNumberInfo)
            getNumberInfo(message)
        elif message.text == '◀️ Назад':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Викторина')
            item2 = types.KeyboardButton('Числа')
            markup.add(item1, item2)
            bot.send_message(message.chat.id, '◀️ Назад', reply_markup=markup)


def getNumberInfo(message):
    try:
        num = int(message.text)
        response = requests.get(f'http://numbersapi.com/{num}/{typeNum}')
        data = str(response.text)
        bot.send_message(message.from_user.id, data)
    except Exception as ex:
        bot.send_message(message.from_user.id, "Неккореткный ввод...")
        print(ex)


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200


@server.route("/")
def index():
    return "<h1>Hello!</h1>"


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

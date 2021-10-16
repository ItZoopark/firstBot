import os

import requests
import telebot
from flask import Flask, request
import json
from telebot import types

TOKEN = "2003680813:AAHB85TfLFidKVKHZFPEaJQsxa2Nzp_we8Y"

APP_URL = f"https://test-itdop-bot2021.herokuapp.com/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

correct_answer = ''

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
    global correct_answer
    if message.chat.type == 'private':
        if message.text == 'Викторина':
            while True:
                try:
                    response = requests.get('https://jservice.io/api/random?count=1')
                    json_str = str(response.json()).replace("\"", "_").replace("\'", "\"")\
                        .replace("_", "\'").replace('None', 'null')
                    json_res = json.loads(json_str)
                    question = json_res[0]["question"]
                    correct_answer = json_res[0]["answer"]
                    print("correct answer ----->>>>>" + correct_answer)
                    bot.send_message(message.from_user.id, question)
                    bot.send_message(message.from_user.id, "Введите ответ:")
                    bot.register_next_step_handler(message, checkAnswer)
                    break
                    # json_res = json.loads()
                except Exception as ex:
                    print(ex)


def checkAnswer(message):
    user_answer = message.text
    if user_answer == correct_answer:
        bot.send_message(message.from_user.id, "Правильно!")
    else:
        bot.send_message(message.from_user.id, "Не верно!")


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

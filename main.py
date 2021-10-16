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
    if message.chat.type == 'private':
        if message.text == 'Викторина':
            while True:
                try:
                    # json_dump = json.dumps(
                    #     '[{"id":88055,"answer":"10","question":"Bo Derek probably knows diamonds rate this on the Mohs scale, which measures hardness","value":200,"airdate":"2009-07-06T12:00:00.000Z","created_at":"2014-02-14T01:53:42.801Z","updated_at":"2014-02-14T01:53:42.801Z","category_id":3953,"game_id":null,"invalid_count":null,"category":{"id":3953,"title":"diamonds are forever","created_at":"2014-02-11T23:05:51.795Z","updated_at":"2014-02-11T23:05:51.795Z","clues_count":15}}]')
                    response = requests.get('https://jservice.io/api/random?count=1')
                    json_str = str(response.json()).replace("\"", "_").replace("\'", "\"").replace("_", "\'").replace('None' , 'null')
                    print(json_str)
                    json_res = json.loads(json_str)
                    print("question: " + json_res[0]['question'])
                    print("answer: " + json_res[0]['answer'])
                    # json_res = json.loads(json_dump)
                    bot.send_message(message.from_user.id, json_res[0]['question'])
                    break
                except Exception as ex:
                    print(ex)
        # if message.text == 'привет!':
        #     bot.send_message(message.from_user.id, 'Здаров!')
        # else:
        #     bot.send_message(message.from_user.id, "давайте знакомится?!")


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

import os
import uuid

import requests
import telebot
from flask import Flask, request
import json
from telebot import types
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

TOKEN = "2003680813:AAHB85TfLFidKVKHZFPEaJQsxa2Nzp_we8Y"

APP_URL = f"https://test-itdop-bot2021.herokuapp.com/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

correct_answer = ''
typeNum = ''

cred = credentials.Certificate("schooldopdb-firebase-adminsdk-q1hlv-e154bb7a75.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://schooldopdb-default-rtdb.europe-west1.firebasedatabase.app/'
})


# изменения

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
        item3 = types.KeyboardButton('БД')
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, f'Привет! <b> {message.from_user.id} </b>'
                         , parse_mode='html', reply_markup=markup)
    except Exception as ex:
        print(ex)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    global correct_answer
    global typeNum
    if message.chat.type == 'private':
        if message.text == 'teacher':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Создать пользователя')
            item2 = types.KeyboardButton('Назначить вопросы')
            item3 = types.KeyboardButton('Получить результаты')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Добро пожаловать в Админ панель!', reply_markup=markup)
        elif message.text == 'Создать пользователя':
            bot.send_message(message.from_user.id, "введите ФИО, userId, класс и букву")
            bot.register_next_step_handler(message, createStudent)
        elif message.text == 'Викторина':
            while True:
                try:
                    response = requests.get('https://jservice.io/api/random?count=1')
                    json_str = str(response.json()).replace("\"", "_").replace("\'", "\"") \
                        .replace("_", "\'").replace('None', 'null')
                    json_res = json.loads(json_str)
                    question = json_res[0]["question"]
                    correct_answer = json_res[0]["answer"]
                    print("correct answer ----->>>>>" + correct_answer)
                    bot.send_message(message.from_user.id, question)
                    bot.send_message(message.from_user.id, "Введите ответ:")
                    bot.register_next_step_handler(message, checkAnswer)
                    break

                except Exception as ex:
                    print(ex)

        elif message.text == 'БД':
            bot.send_message(message.from_user.id, "Выберите раздел")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Отправить')
            item2 = types.KeyboardButton('Получить')
            back = types.KeyboardButton('◀️ Назад')
            markup.add(item1, item2, back)
            bot.send_message(message.chat.id, 'Работа с БД', reply_markup=markup)
        elif message.text == 'Отправить':
            bot.send_message(message.from_user.id, "Напишите текст...")
            bot.register_next_step_handler(message, saveInFirebase)
        elif message.text == 'Получить':
            try:
                answer = str(db.reference('schooldopdb-default-rtdb/').get()).replace("\'", "\"")
                answer_json = json.loads(answer)
                for answer_id in answer_json:
                    data_str = str(db.reference(f'schooldopdb-default-rtdb/{answer_id}').get()).replace("\'", "\"")
                    data = json.loads(data_str)
                    bot.send_message(message.from_user.id, data["message"])
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
        elif message.text == 'Факт':
            typeNum = 'trivia'
            bot.send_message(message.from_user.id, "Напишите число, про которое хотите узнать...")
            bot.register_next_step_handler(message, getNumberInfo)
        elif message.text == '◀️ Назад':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Викторина')
            item2 = types.KeyboardButton('Числа')
            markup.add(item1, item2)
            bot.send_message(message.chat.id, '◀️ Назад', reply_markup=markup)


def saveInFirebase(message):
    try:
        message_id = uuid.uuid4().hex
        new_message = {
            "message": str(message.text)
        }
        db.reference('schooldopdb-default-rtdb/' + message_id).set(new_message)
        bot.send_message(message.from_user.id, "Данные сохранены!")
    except Exception as ex:
        print(ex)


def createStudent(message):
    data = str(message.text).split(' ')
    fio = data[0] + data[1]
    userId = data[2]
    num = data[3]
    letter = data[4]
    print(fio)
    print(userId)
    print(num)
    print(letter)
    response = requests.get(f'https://school-estimate-django-rest.herokuapp.com/api/v1/?num={num}&letter={letter}')
    # response_json_str = str(response.json()).replace("\'", "\"").replace('None', 'null')
    print(response)
    # json_res = json.loads(response_json_str)
    # grade_id = json_res["id"]
    # response = requests.post('https://school-estimate-django-rest.herokuapp.com/api/v1/student/',
    #                          data={'name': fio, 'userId': userId, 'grade': grade_id})


def getNumberInfo(message):
    try:
        if typeNum == 'math' or typeNum == 'trivia':
            num = int(message.text)
        response = requests.get(f'http://numbersapi.com/{num}/{typeNum}')
        data = response.text
        bot.send_message(message.from_user.id, data)
    except Exception as ex:
        bot.send_message(message.from_user.id, "Неккореткный ввод...")
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

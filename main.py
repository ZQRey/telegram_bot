import telebot
import config
import mysql.connector
import logging
import mysql
from mysql.connector import errorcode
import sys
import datetime
from datetime import datetime
from telebot import types

# Подключение к боту
bot = telebot.TeleBot(config.TOKEN)

# Работа с файлом
########################################################################################################################
# Файл с логами
logger = telebot.logger
formatter = logging.Formatter('[%(asctime)s] %(thread)d {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                              '%m-%d %H:%M:%S')
ch = logging.StreamHandler(sys.stdout)
logger.addHandler(ch)
logger.setLevel(logging.INFO)
ch.setFormatter(formatter)


def write_file(text):
    now = datetime.now()
    log_file = open('err.txt', 'a')
    log_file.write(str(now) + text + '\n')
    print(text)

# Работа с базой данных
########################################################################################################################
try:
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd=config.passwd_mysql,
        port='3306',
        database='db_polka',
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        write_file('Ошибка подключения к БД: Проблема с логином или паролем')
        sys.exit()
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        write_file('БД не найдена')
        sys.exit()
    else:
        write_file('Ошибка БД: {0}'.format(err))
        print('Ошибка БД: {0}'.format(err))
        sys.exit()

write_file('Подключение к базе данных выполнено ' + str(mydb))
print('Подключение к базе данных выполнено ' + str(mydb))

cursor = mydb.cursor()

# Работа с ботом
########################################################################################################################
print('Бот запущен!')
write_file('Бот запущен!')

# Словарь работы с данными пользователя
user_data = {}

# Кнопки
# Главное меню
gl_markup = telebot.types.ReplyKeyboardMarkup(True, True)
gl_markup.row('Отправить заявку')
gl_markup.row('Описание')
# Типы выполняемых работ
type_markup = telebot.types.ReplyKeyboardMarkup(True, True)
type_markup.add('Отказ оборудования или связи (включая интернет)')
type_markup.add('Учетные записи, логины и пароли')
type_markup.add('Консультация и обучение')
# Отмена
back_markup = telebot.types.ReplyKeyboardMarkup(True, True)
back_markup.add('Отмена')
# Отработка заявки
# work_yes = types.InlineKeyboardButton(text='Взята в работу', callback_data='Взята')
# work_no = types.InlineKeyboardButton(text='Отказано', callback_data='Отказано')
# work_status = types.InlineKeyboardMarkup()
# work_status.row(work_yes, work_no)


class User:
    def __init__(self, first_name):
        self.first_name = first_name
        self.number = ''
        self.profesion = ''
        self.otdelenie = ''


# Обработка команд
@bot.message_handler(commands=['start'])
def start_message(message):
    print('Пользователь с именем: {0.first_name} никнеймом: {1.username} активировал бота'.format(message.from_user,
                                                                                                  message.from_user))
    bot.send_message(message.chat.id, "Выберете пункт меню для продолжения работы с ботом.\n"
                                      "Для информации о работе с ботом выберете пункт «Описание».",
                     reply_markup=gl_markup)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "Help message")


@bot.message_handler(content_types=['text'])
def menu_item(message):
    print('Пользователь {0.first_name} отправил сообщение {1}'.format(message.from_user, message.text))
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_data[user_id] = User(message.text)
    if message.text.lower() == 'описание':
        bot.send_message(chat_id, text=config.info, reply_markup=gl_markup)
    elif message.text.lower() == 'отправить заявку':
        # Проверка пользователя зареган или нет
        sql = f"SELECT * FROM regs WHERE user_id = {chat_id}"
        cursor.execute(sql)
        existsUser = cursor.fetchone()
        # Если нету, то добавить в БД
        if (existsUser == None):
            msg = bot.send_message(chat_id, 'Пожалуйста представьтесь')
            bot.register_next_step_handler(msg, reg_name)
        else:

            msg = bot.send_message(chat_id, 'Здравствуйте {0}. Опишите в чем будет заключаться работа\n'
                                            'Для отмены операции напишите отмена или нажмите соответствующее меню'
                                   .format(existsUser[1]), reply_markup=type_markup)
            bot.register_next_step_handler(msg, type_work)
    elif message.text.lower() == '📄просмотреть заявки':
        try:
            # Подключение к БД и сбор информаци о заявках пользователя
            user_id = message.from_user.id
            if user_id == config.admin_id:
                sql = "SELECT * FROM work_list"
                cursor.execute(sql)
                description = cursor.fetchall()
                mydb.commit()

                # Сделать проверку на пустую строку
                for rez in description:
                    bot.send_message(message.chat.id,
                                     'Номер заявки: {0}\nДата отправки: {2}\nВид работ: {3}'
                                     '\nТекст заявки: {1}\nСтатус заявки: {4}'.format(rez[0], str(rez[1]), rez[4],
                                                                                      str(rez[3]), str(rez[5])))
            else:
                sql = "SELECT * FROM work_list WHERE telegram_user_id = {0}".format(user_id)
                cursor.execute(sql)
                description = cursor.fetchall()
                mydb.commit()

                # Сделать проверку на пустую строку
                for rez in description:
                    bot.send_message(message.chat.id,
                                     'Номер заявки: {0}\nДата отправки: {2}\nВид работ: {3}'
                                     '\nТекст заявки: {1}'.format(rez[0], str(rez[1]), rez[4], str(rez[3])))
        except Exception as e:
            write_file('Ошибка показа заявок: функция вывела ошибку ' + str(e))
            bot.reply_to(message, 'Ошибка показа заявок: функция вывела ошибку\n' + str(e))
    elif message.text.lower() == 'send_user':
        msg = bot.send_message(chat_id, 'Выполнение отправки сообщения от админа')
        bot.register_next_step_handler(msg, admin_send_message)
    elif message.text.lower() == 'написать отзыв':
        msg = bot.send_message(chat_id, 'Сейчас вы можете написать отзыв о работе компании')
        bot.register_next_step_handler(msg, send_in_jurnal)
    elif message.text == 'Посмотреть отзывы':
        try:
            sql = "SELECT * FROM jurnal"
            cursor.execute(sql)
            text = cursor.fetchall()

            # Сделать проверку на пустую строку
            for rez in text:
                if rez[0] is not None:
                    bot.send_message(message.chat.id,
                                     'Номер отзыва: {0}\nТекст отзыва: {1}'.format(str(rez[0]), str(rez[1])))
        except Exception as e:
            write_file('Ошибка модуля просмотра отзывов ' + str(e))
    else:
        bot.send_message(chat_id, 'Повторите запрос. Напишите небходимый вам пункт меню или выберите его.')


# Методы (функции)
########################################################################################################################
# ---------------------------------------------Регистрация пользователя------------------------------------------------#
# Регистрация имени и запрос номера
def reg_name(message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)
        msg = bot.send_message(message.chat.id, 'Введите ваш номер телефона')
        bot.register_next_step_handler(msg, registration)
    except Exception as e:
        write_file('Ошибка регистрации: проблема с функцией регистрации имени ' + str(e))
        print(e)
        bot.reply_to(message, 'Ошибка регистрации: проблема с функцией регистрации имени')

# Сбор конечных данных и запись в БД
def registration(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.number = message.text
        number = int(message.text[1:])
        user_data[number] = User(message.text)
        sql = "INSERT INTO regs (first_name, number_phone,  user_id) VALUES (%s, %s, %s)"
        val = (user.first_name, message.text, message.chat.id)
        cursor.execute(sql, val)
        mydb.commit()
        msg = bot.send_message(message.chat.id, 'Вы зарегистрированы! \nВыберите пункт меню.', reply_markup=type_markup)
        bot.register_next_step_handler(msg, type_work)

    except Exception as e:
        write_file('Ошибка регистрации: функция финальной регистрации вывела ошибку ' + str(e))
        print(e)
        bot.reply_to(message, 'Ошибка регистрации: не верно введен номер телефона')


# --------------------------------------------------END----------------------------------------------------------------#
# -----------------------------------------Отправка_заявки_на_выполнение_работ-----------------------------------------#
# Выбор типа работ
def type_work(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.type_work = message.text
        msg = bot.send_message(message.chat.id, 'Введите описание работ '
                                                'или нажмите кнопку отмены', reply_markup=back_markup)
        bot.register_next_step_handler(msg, description_work)
    except Exception as e:
        write_file('Ошибка модуля: Тип работ' + str(e))
        bot.send_message(message.chat.id, 'Ошибка модуля: Тип работ')


# Создание заявки
def description_work(message):
    try:
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, reply_markup=gl_markup)
        else:
            user_id = message.from_user.id
            user = user_data[user_id]
            date_send_msg = datetime.now()
            # Вставка информации в БД
            sql = "INSERT INTO work_list (description, telegram_user_id, type_work, date_send_msg) VALUES (%s, %s, %s, %s)"
            val = (message.text, user_id, user.type_work, date_send_msg)
            cursor.execute(sql, val)
            mydb.commit()

            # Выбор имени пользователя из БД
            sql = "SELECT first_name FROM regs WHERE user_id = {0}".format(user_id)
            cursor.execute(sql)
            existsUser = cursor.fetchone()

            # Выбор информации о номере заявки из БД
            sql = 'SELECT id FROM work_list WHERE telegram_user_id = {0}'.format(user_id)
            cursor.execute(sql)
            number_desc = cursor.fetchall()

            # Выбор информации о номере заявки из БД
            sql = 'SELECT number_phone FROM regs WHERE user_id = {0}'.format(user_id)
            cursor.execute(sql)
            number_phone = cursor.fetchall()

            # Вывод информации об успешно созданой заявке и отправка админу (Возможно дает сбой)
            bot.send_message(config.admin_id, text=('Новая заявка {0}\nДата отправки: {6}'
                                                    '\nПользователь: {1}\nНомер телефона: {2}'
                                                    '\nЧат с пользователем: @{3}\nВид работ: {4}'
                                                    '\nОписание работ: {5}').format(str(number_desc[-1])[1:3],
                                                                                    existsUser[0],
                                                                                    str(number_phone[0]),
                                                                                    message.from_user.username,
                                                                                    user.type_work,
                                                                                    message.text,
                                                                                    datetime.today()))
            #            bot.send_message(config.moder_id, text=('Новая заявка {0}\n Пользователь: {1}\nНомер телефона: {2}'
            #                                                    '\nЧат с пользователем: @{3}\nВид работ: {4}'
            #                                                    '\nОписание работ: {5}').format(str(number_desc[-1])[1:3],
            #                                                                                    existsUser[0],
            #                                                                                    str(number_phone[0]),
            #                                                                                    message.from_user.username,
            #                                                                                    user.type_work,
            #                                                                                    message.text))
            bot.send_message(message.chat.id,
                             'Ваша заявка под номером #{0} успешно зарегистрирована.\n'
                             .format(str(number_desc[-1])[1:3]),
                             reply_markup=gl_markup)  # Возможно нужно добавить номер заявки

    except Exception as e:
        write_file('Ошибка отправки заявки: функция вывела ошибку' + str(e))
        bot.reply_to(message, 'Ошибка отправки заявки: функция вывела ошибку\n' + str(e))

# Выбор действия с заявкой
#@bot.callback_query_handler(func=lambda call:True)
#def call_status_work(call):
#    if call.data == 'Взята':
#
# ------------------------------------------------------END------------------------------------------------------------#
# -----------------------------------------------Отправка сообщений от админа пользователям----------------------------#

def admin_send_message(message):
    try:
        sql = "SELECT user_id FROM regs"
        cursor.execute(sql)
        description = cursor.fetchall()
        mydb.commit()
        for temp in description:
            bot.send_message(chat_id=temp, text=message.text)
            print(temp)
    except Exception as e:
        write_file('Ошибка модуля: Отправка сообщения от админа ' + str(e))
        bot.send_message(message.chat.id, 'Ошибка модуля: Отправка сообщения от админа')
        print(str(e))


# --------------------------------------------------Журнал отзывов-----------------------------------------------------#
def send_in_jurnal(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        sql = "INSERT INTO jurnal (message, user_id) VALUES (%s, %s)"
        val = (message.text, message.chat.id)
        cursor.execute(sql, val)
        mydb.commit()
        bot.send_message(config.admin_id, 'У вас новый отзыв! \n{0}'.format(message.text))
        #        bot.send_message(config.moder_id, 'У вас новый отзыв! \n{0}'.format(message.text))
        bot.send_message(message.chat.id, 'Спасибо за отзыв о работе компании')
    except Exception as e:
        write_file("Ошибка отправки отзыва " + str(e))


########################################################################################################################
# Код что ниже не трогать!
# Сохранение предыдущего запроса
bot.enable_save_next_step_handlers(delay=5)

# Запуск продолжения кода
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)

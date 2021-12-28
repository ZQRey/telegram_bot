import telebot
import config
import mysql.connector
import logging
import mysql
from mysql.connector import errorcode
import sys
import datetime
from datetime import datetime
import post_send
import get_send

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
gl_markup.row('Информация о заявке')
gl_markup.row('Описание')
# Типы выполняемых работ
type_markup = telebot.types.ReplyKeyboardMarkup(True, True)
type_markup.add('Отказ оборудования или связи (включая интернет)')
type_markup.add('Учетные записи, логины и пароли')
type_markup.add('Консультация и обучение')
# Отмена
back_markup = telebot.types.ReplyKeyboardMarkup(True, True)
back_markup.add('Отмена')
# reply_markup для выбора корпуса
korp_markup = telebot.types.ReplyKeyboardMarkup(True, True)
korp_markup.add('Главный корпус')
korp_markup.add('Детский корпус')
korp_markup.add('Дневной стационар')
korp_markup.add('Отмена')


# Отработка заявки
# work_yes = types.InlineKeyboardButton(text='Взята в работу', callback_data='Взята')
# work_no = types.InlineKeyboardButton(text='Отказано', callback_data='Отказано')
# work_status = types.InlineKeyboardMarkup()
# work_status.row(work_yes, work_no)

class User:
    def __init__(self, first_name):
        self.category = 'Отказ оборудования или связи (включая интернет)'
        self.name = first_name
        self.priority = 'medium'
        self.number_kab = '-'
        self.number_phone = '-'
        self.korpus = 'Главный корпус'
        self.theme = '-'
        self.msg = '-'


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
            msg = bot.send_message(chat_id, 'Пожалуйста введите ваше ФИО')
            bot.register_next_step_handler(msg, reg_name)
        else:

            msg = bot.send_message(chat_id, 'Здравствуйте {0}. Опишите в чем будет заключаться работа\n'
                                            'Для отмены операции напишите отмена или нажмите соответствующее меню'
                                   .format(existsUser[1]), reply_markup=type_markup)
            bot.register_next_step_handler(msg, number_cab)
    # Разработать модуль для просмотра заявки!!! admin_id на данный момент нет
    elif message.text.lower() == 'просмотреть заявки':
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
    elif message.text.lower() == 'информация о заявке':
        msg = bot.send_message(chat_id, 'Сбор информации о заявке, введите номер заявки.\n'
                                        'Формат: ХХХХ-ХХХХ-ХХХХ')
        bot.register_next_step_handler(msg, info_request)
    else:
        bot.send_message(chat_id, 'Повторите запрос. Напишите небходимый вам пункт меню или выберите его.',
                         reply_markup=gl_markup)


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
        bot.reply_to(message, 'Ошибка регистрации: проблема с функцией регистрации имени' + str(e) +
                     "\nСвяжитесь с техподдержкой и передайте ошибку")


# Сбор конечных данных и запись в БД
def registration(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.number_phone = message.text
        number = int(message.text[1:])
        user_data[number] = User(message.text)
        sql = "INSERT INTO regs (first_name, number_phone,  user_id) VALUES (%s, %s, %s)"
        val = (user.name, message.text, message.chat.id)
        cursor.execute(sql, val)
        mydb.commit()
        msg = bot.send_message(message.chat.id, 'Вы зарегистрированы! \nВыберите пункт меню.', reply_markup=type_markup)
        bot.register_next_step_handler(msg, number_cab)

    except Exception as e:
        write_file('Ошибка регистрации: функция финальной регистрации вывела ошибку ' + str(e))
        print(e)
        bot.reply_to(message, 'Ошибка регистрации: не верно введен номер телефона', reply_markup=gl_markup)


# --------------------------------------------------END----------------------------------------------------------------#
# -----------------------------------------Отправка_заявки_на_выполнение_работ-----------------------------------------#
# Прием категории и ввод номера кабинета
def number_cab(message):
    try:
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Возврат в меню', reply_markup=gl_markup)
        user_id = message.from_user.id
        user = user_data[user_id]
        user.category = message.text
        msg = bot.send_message(message.chat.id, 'Введите номер кабинета '
                                                'или нажмите кнопку отмены', reply_markup=back_markup)
        bot.register_next_step_handler(msg, corpus_otd)
    except Exception as e:
        write_file('Ошибка модуля: номер кабинета' + str(e))
        bot.send_message(message.chat.id, 'Ошибка модуля: номер кабинета ' + str(e) +
                         "\nСвяжитесь с техподдержкой и передайте ошибку", reply_markup=gl_markup)


# Прием номера кабинета и выбор корпуса
def corpus_otd(message):
    try:
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Возврат в меню', reply_markup=gl_markup)
        user_id = message.from_user.id
        user = user_data[user_id]
        user.number_kab = message.text
        msg = bot.send_message(message.chat.id, 'Выберите корпус '
                                                'или нажмите кнопку отмены',
                               reply_markup=korp_markup)  # reply_markup для выбора корпуса
        bot.register_next_step_handler(msg, theme_zay)
    except Exception as e:
        write_file('Ошибка модуля: Тип работ' + str(e))
        bot.send_message(message.chat.id, 'Ошибка модуля: Тип работ ' + str(e) +
                         "\nСвяжитесь с техподдержкой и передайте ошибку", reply_markup=gl_markup)


# Прием номера корпуса и ввод темы заявки
def theme_zay(message):
    try:
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Возврат в меню', reply_markup=gl_markup)
        user_id = message.from_user.id
        user = user_data[user_id]
        user.korpus = message.text
        msg = bot.send_message(message.chat.id, 'Введите тему заявки '
                                                'или нажмите кнопку отмены', reply_markup=back_markup)
        bot.register_next_step_handler(msg, description)
    except Exception as e:
        write_file('Ошибка модуля: номер кабинета' + str(e))
        bot.send_message(message.chat.id, 'Ошибка модуля: номер кабинета ' + str(e) +
                         "\nСвяжитесь с техподдержкой и передайте ошибку", reply_markup=gl_markup)


# Прием номера корпуса и ввод темы заявки
def description(message):
    try:
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Возврат в меню', reply_markup=gl_markup)
        user_id = message.from_user.id
        user = user_data[user_id]
        user.theme = message.text
        msg = bot.send_message(message.chat.id, 'Опишите вашу проблему '
                                                'или нажмите кнопку отмены', reply_markup=back_markup)
        bot.register_next_step_handler(msg, send_zayvka)
    except Exception as e:
        write_file('Ошибка модуля: номер кабинета' + str(e))
        bot.send_message(message.chat.id, 'Ошибка модуля: номер кабинета ' + str(e) +
                         "\nСвяжитесь с техподдержкой и передайте ошибку", reply_markup=gl_markup)


# Описание проблемы
def send_zayvka(message):
    sql = f"SELECT * FROM regs WHERE user_id = {message.chat.id}"
    cursor.execute(sql)
    existsUser = cursor.fetchone()
    try:
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Возврат в меню', reply_markup=gl_markup)
        else:

            user_id = message.from_user.id
            user = user_data[user_id]
            user.msg = message.text
            number_zayavki = post_send.create(category=user.category, name=existsUser[1], priority=user.priority,
                                              number_kab=user.number_kab,
                                              number_phone=existsUser[2], korpus=user.korpus, theme=user.theme,
                                              msg=user.msg)
            bot.send_message(existsUser[0], f'Ваша заявка принята под номером {number_zayavki}', reply_markup=gl_markup)
    except Exception as e:
        write_file('Ошибка отправки заявки: функция вывела ошибку ' + str(e))
        bot.send_message(message, 'Ваша заявка успешно создана, ожидайте', reply_markup=gl_markup)


# Выбор действия с заявкой
# @bot.callback_query_handler(func=lambda call:True)
# def call_status_work(call):
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
        bot.send_message(message.chat.id, 'Ошибка модуля: Отправка сообщения от админа' +
                         "\nСвяжитесь с техподдержкой и передайте ошибку")
        print(str(e))


# ---------------------------------------------Информация о заявке-----------------------------------------------------#
def temp(message):
    try:
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Возврат в меню', reply_markup=gl_markup)
        msg = bot.send_message(message.chat.id, 'Введите номер заявки в формате "ХХХХ-ХХХХ-ХХХХ"',
                               reply_markup=back_markup)
        bot.register_next_step_handler(msg, info_request)
    except Exception as e:
        write_file('Ошибка модуля: номер кабинета' + str(e))
        bot.send_message(message.chat.id, 'Ошибка модуля: информация о заявке ' + str(e) +
                         "\nСвяжитесь с техподдержкой и передайте ошибку", reply_markup=gl_markup)


def info_request(message):
    try:
        sql = f"SELECT * FROM regs WHERE user_id = {message.chat.id}"
        cursor.execute(sql)
        existsUser = cursor.fetchone()
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Возврат в меню', reply_markup=gl_markup)
        if len(message.text) == 12:
            data = get_send.get_send(message.text)
            bot.send_message(existsUser[0], "ID: {0}\n"
                                        "Статус заявки: {1}\n"
                                        "Дата создания: {2}\n"
                                        "Дата обновления: {3}\n"
                                        "Последний оставивший сообщение: {4}".format(data.pop('ID'), data.pop('Status'),
                                                                                     data.pop('Create'),
                                                                                     data.pop('Update'),
                                                                                     data.pop('Last_send')),
                         reply_markup=gl_markup)
        else:
            bot.send_message(existsUser[0], 'Вы ввели не правильный номер заявки', reply_markup=gl_markup)
    except Exception as e:
        write_file("Ошибка отправки информации " + str(e))


########################################################################################################################
# Код что ниже не трогать!
# Сохранение предыдущего запроса
bot.enable_save_next_step_handlers(delay=8)

# Запуск продолжения кода
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)

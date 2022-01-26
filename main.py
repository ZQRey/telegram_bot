import telebot
import config
import logging
import sys
import datetime
from datetime import datetime
import post_send
import get_send
import connection_db

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
    log_file = open('log.txt', 'a')
    log_file.write(str(now) + text + '\n')


def write_msg(text):
    now = datetime.now()
    log_file = open('msg.txt', 'a')
    log_file.write(str(now) + ' ' + text + '\n')


# Работа с базой данных
########################################################################################################################


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
type_markup.add('Учетные записи, роли, логины и пароли')
type_markup.add('Консультация и обучение')
# Отмена
back_markup = telebot.types.ReplyKeyboardMarkup(True, True)
back_markup.add('Отмена')
# reply_markup для выбора корпуса
korp_markup = telebot.types.ReplyKeyboardMarkup(True, True)
korp_markup.add('Главный корпус')
korp_markup.add('Детский корпус')
korp_markup.add('Дневной стационар')


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

def type_day():
    time_now = datetime.now().hour
    if 19 <= time_now <= 23:
        temp = 'Добрый вечер'
    elif 0 <= time_now <= 5:
        temp = 'Доброй ночи'
    elif 6 <= time_now <= 11:
        temp = 'Доброе утро'
    elif 12 <= time_now <= 18:
        temp = "Добрый день"
    else:
        temp = 'Здравствуйте'
    return temp

# Обработка команд
@bot.message_handler(commands=['start'])
def start_message(message):
    print('Пользователь с именем: {0.first_name} никнеймом: {1.username} активировал бота'.format(message.from_user,
                                                                                                  message.from_user))
    write_msg('Пользователь с именем: {0.first_name} никнеймом: {1.username} активировал бота'
              .format(message.from_user, message.from_user))
    temp = type_day()
    bot.send_message(message.chat.id, f"{temp}! Выберете пункт меню для продолжения работы с ботом.\n"
                                      "Для получения краткой информации о работе с ботом выберете пункт «Описание».",
                     reply_markup=gl_markup)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "Help message")


@bot.message_handler(content_types=['text'])
def menu_item(message):
    print('Пользователь {0.first_name} отправил сообщение {1}'.format(message.from_user, message.text))
    write_msg('Пользователь {0.first_name} отправил сообщение {1}'.format(message.from_user, message.text))
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_data[user_id] = User(message.text)
    if message.text.lower() == 'описание':
        bot.send_message(chat_id, text=config.info, reply_markup=gl_markup)
    elif message.text.lower() == 'отправить заявку':
        # Проверка пользователя зареган или нет
        cursor = connection_db.connection_db()
        existsUser = connection_db.search_user(cursor[0], message.chat.id)
        # Если нету, то добавить в БД
        if (existsUser == None):
            msg = bot.send_message(chat_id, 'Пожалуйста введите ваше ФИО')
            bot.register_next_step_handler(msg, reg_name)
        else:
            temp = type_day()
            msg = bot.send_message(chat_id, '{1} {0}! Выберите категорию вашей проблемы\n'
                                   .format(existsUser[1], temp), reply_markup=type_markup)
            bot.register_next_step_handler(msg, number_cab)
    elif message.text.lower() == 'информация о заявке':
        msg = bot.send_message(chat_id, 'Сбор информации о заявке, введите номер заявки.\n'
                                        'Формат: ХХХ-ХХХ-ХХХХ')
        bot.register_next_step_handler(msg, info_request)
    else:
        bot.send_message(chat_id, 'Повторите запрос. Напишите небходимый вам пункт меню или выберите его.',
                         reply_markup=gl_markup)


########################################################################################################################

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
        cursor = connection_db.connection_db()
        connection_db.reg_user(cursor[0], cursor[1], user.name, message.text, message.chat.id)
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
        msg = bot.send_message(message.chat.id, 'Введите номер кабинета ', reply_markup=None)
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
        msg = bot.send_message(message.chat.id, 'Выберите корпус ',
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
        msg = bot.send_message(message.chat.id, 'Введите тему заявки ', reply_markup=None)
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
        msg = bot.send_message(message.chat.id, 'Опишите вашу проблему ', reply_markup=None)
        bot.register_next_step_handler(msg, send_zayvka)
    except Exception as e:
        write_file('Ошибка модуля: номер кабинета' + str(e))
        bot.send_message(message.chat.id, 'Ошибка модуля: номер кабинета ' + str(e) +
                         "\nСвяжитесь с техподдержкой и передайте ошибку", reply_markup=gl_markup)


# Описание проблемы
def send_zayvka(message):
    cursor = connection_db.connection_db()
    existsUser = connection_db.user_data(cursor[0], message.chat.id)
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
            write_msg(f' Пользователь с id {message.chat.id}, именем {existsUser[1]} и номером телефона {existsUser[2]}'
                      f' отправил оставил заявку: Тема: {user.theme} Описание: {user.msg}')
    except Exception as e:
        write_file('Ошибка отправки заявки: функция вывела ошибку ' + str(e))
        bot.send_message(message, 'Ваша заявка успешно создана, ожидайте', reply_markup=gl_markup)


# ------------------------------------------------------END------------------------------------------------------------#
# -----------------------------------------------Отправка сообщений от админа пользователям----------------------------#

#   def admin_send_message(message):
#       try:
#           sql = "SELECT user_id FROM regs"
#           cursor.execute(sql)
#           description = cursor.fetchall()
#           mydb.commit()
#           for temp in description:
#               bot.send_message(chat_id=temp, text=message.text)
#               print(temp)
#       except Exception as e:
#           write_file('Ошибка модуля: Отправка сообщения от админа ' + str(e))
#           bot.send_message(message.chat.id, 'Ошибка модуля: Отправка сообщения от админа' +
#                            "\nСвяжитесь с техподдержкой и передайте ошибку")
#           print(str(e))


# ---------------------------------------------Информация о заявке-----------------------------------------------------#
def temp(message):
    try:
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Возврат в меню', reply_markup=gl_markup)
        msg = bot.send_message(message.chat.id, 'Введите номер заявки в формате "ХХХХ-ХХХХ-ХХХХ"',
                               reply_markup=None)
        bot.register_next_step_handler(msg, info_request)
    except Exception as e:
        write_file('Ошибка модуля: номер кабинета' + str(e))
        bot.send_message(message.chat.id, 'Ошибка модуля: информация о заявке ' + str(e) +
                         "\nСвяжитесь с техподдержкой и передайте ошибку", reply_markup=gl_markup)


def info_request(message):
    try:
        cursor = connection_db.connection_db()
        existsUser = connection_db.request(cursor[0], message.chat.id)
        if message.text.lower() == 'отмена':
            bot.send_message(message.chat.id, 'Возврат в меню', reply_markup=gl_markup)
        if len(message.text) == 12:
            data = get_send.get_send(message.text)
            bot.send_message(existsUser[0], "ID: {0}\n"
                                            "Статус заявки: {1}\n"
                                            "Дата создания: {2}\n"
                                            "Дата обновления: {3}\n"
                                            "Последний оставивший сообщение: {4}\n"
                                            "Последнее сообщение в заявке".format(data.pop('ID'),
                                                                                         data.pop('Status'),
                                                                                         data.pop('Create'),
                                                                                         data.pop('Update'),
                                                                                         data.pop('Last_send')),
                             reply_markup=gl_markup)
        else:
            bot.send_message(existsUser[0], 'Вы ввели не правильный номер заявки', reply_markup=gl_markup)
    except Exception:
        bot.send_message(message.chat.id, 'Данные не отображаются. Возможно ваша заявка была решена.'
                         , reply_markup=gl_markup)


########################################################################################################################
# Код что ниже не трогать!
# Сохранение предыдущего запроса
bot.enable_save_next_step_handlers(delay=8)

# Запуск продолжения кода
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)

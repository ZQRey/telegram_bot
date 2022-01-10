# Работа с базой данных
########################################################################################################################
import mysql
from mysql.connector import errorcode
from datetime import datetime
import sys
import config

def write_file(text):
    now = datetime.now()
    log_file = open('log.txt', 'a')
    log_file.write(str(now) + text + '\n')
    print(text)

def search_user(cursor, chat_id):
    sql = f"SELECT * FROM regs WHERE user_id = {chat_id}"
    cursor.execute(sql)
    existsUser = cursor.fetchone()
    cursor.close()
    return existsUser

def reg_user(cursor, mydb, first_name, number_phone,  user_id):
    sql = "INSERT INTO regs (first_name, number_phone,  user_id) VALUES (%s, %s, %s)"
    val = (first_name, number_phone,  user_id)
    cursor.execute(sql, val)
    mydb.commit()
    cursor.close()
    mydb.close()

def user_data(cursor, chat_id):
    sql = f"SELECT * FROM regs WHERE user_id = {chat_id}"
    cursor.execute(sql)
    existsUser = cursor.fetchone()
    cursor.close()
    return existsUser

def request(cursor, chat_id):
    sql = f"SELECT * FROM regs WHERE user_id = {chat_id}"
    cursor.execute(sql)
    existsUser = cursor.fetchone()
    cursor.close()
    return existsUser

def connection_db():
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
    return cursor, mydb

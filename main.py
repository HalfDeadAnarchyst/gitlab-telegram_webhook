from config import api_key
import telebot
from requests import exceptions


bot = telebot.TeleBot(api_key)


def replace_file_line(header, string):
    list_file = open("user_list.txt", "r")
    lines = list_file.readlines()
    list_file.close()
    list_file = open("user_list.txt", "w")
    for line in lines:
        temp_list = line.split(",")
        if temp_list[0] == header:
            list_file.write(string)
        else:
            list_file.write(line)
    list_file.close()
    return 0


def get_user_dict():
    user_dict = {}
    list_file = open("user_list.txt", "r")
    lines = list_file.readlines()
    for line in lines:
        temp_list = line.split(",")
        user_dict[temp_list[0]] = temp_list
    list_file.close()
    return user_dict


def change_user_config(call, option):
    user_dict = get_user_dict()
    str_to_write = ''
    if user_dict[call.message.chat.username][option] == '0':
        user_dict[call.message.chat.username][option] = '1'
    else:
        user_dict[call.message.chat.username][option] = '0'
    str_to_write += call.message.chat.username + ',' + str(call.message.chat.id) + ',' + user_dict[call.message.chat.username][2] + ',' + user_dict[call.message.chat.username][3] + ',' + user_dict[call.message.chat.username][4] + ',' + user_dict[call.message.chat.username][5] + ',' + user_dict[call.message.chat.username][6] + ',\n'
    header_to_write = user_dict[call.message.chat.username][0]
    replace_file_line(header_to_write, str_to_write)

    return_str = 'Вы '
    if user_dict[call.message.chat.username][option] == '1':
        return_str += 'подписались на уведомления'
    else:
        return_str += 'отписались от уведомлений'

    if option == 3:
        return_str += ' коммитов'
    elif option == 4:
        return_str += ' сборок'
    elif option == 5:
        return_str += ' карточек'
    elif option == 6:
        return_str += ' вики-страниц'
    return return_str


def make_keyboard(message):
    # add keyboard
    keyboard0 = telebot.types.InlineKeyboardMarkup()

    user_dict = get_user_dict()

    if user_dict[message.chat.username][2] == '0':
        str1 = 'Вкл. общие уведомления'
    else:
        str1 = 'Выкл. общие уведомления'

    if user_dict[message.chat.username][3] == '0':
        str2 = 'Вкл. уведомления коммитов'
    else:
        str2 = 'Выкл. уведомления коммитов'

    if user_dict[message.chat.username][4] == '0':
        str3 = 'Вкл. уведомления сборок'
    else:
        str3 = 'Выкл. уведомления сборок'

    if user_dict[message.chat.username][5] == '0':
        str4 = 'Вкл. уведомления карточек'
    else:
        str4 = 'Выкл. уведомления карточек'

    if user_dict[message.chat.username][6] == '0':
        str5 = 'Вкл. уведомления вики-страниц'
    else:
        str5 = 'Выкл. уведомления вики-страниц'

    key_subscribe = telebot.types.InlineKeyboardButton(text=str1, callback_data='subscribe')
    keyboard0.add(key_subscribe)

    key_commits = telebot.types.InlineKeyboardButton(text=str2, callback_data='commits')
    keyboard0.add(key_commits)

    key_builds = telebot.types.InlineKeyboardButton(text=str3, callback_data='builds')
    keyboard0.add(key_builds)

    key_issues = telebot.types.InlineKeyboardButton(text=str4, callback_data='issues')
    keyboard0.add(key_issues)

    key_wiki_pages = telebot.types.InlineKeyboardButton(text=str5, callback_data='wiki-pages')
    keyboard0.add(key_wiki_pages)

    return keyboard0


# Команда \start
@bot.message_handler(commands=['start'])
def start_message(message):
    print(message)
    print("\n")

    # check user on already existing and add if not
    user_dict = get_user_dict()

    if user_dict.get(message.chat.username, "empty") == "empty":
        list_file = open("user_list.txt", "a+")
        list_file.write(str(message.chat.username + ',' + str(message.chat.id) + ',0,0,0,0,0,\n'))
        list_file.close()

    keyboard0 = make_keyboard(message)

    # activate keyboard
    bot.send_message(message.chat.id, 'Приветствую. \nЯ - служба отчётности компании Rotek.'
                                      '\nЕсли вы не являетесь сотрудником компании Rotek,'
                                      ' то попрошу вас уйти и забыть меня.',
                     reply_markup=keyboard0, parse_mode="Markdown")


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "subscribe":
        msg = change_user_config(call, 2)
    if call.data == "commits":
        msg = change_user_config(call, 3)
    if call.data == "builds":
        msg = change_user_config(call, 4)
    if call.data == "issues":
        msg = change_user_config(call, 5)
    if call.data == "wiki-pages":
        msg = change_user_config(call, 6)
    keyboard0 = make_keyboard(call.message)
    bot.send_message(call.message.chat.id, msg, reply_markup=keyboard0, parse_mode="Markdown")


while True:
    try:
        bot.polling(none_stop=True)

    except exceptions.ConnectionError as e:
        print(e)


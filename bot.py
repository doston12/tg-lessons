import time
import telebot
from telebot import types
import config

knownUser = []
userStep = {}

commands = {
    'start',
    'help',
    'sendLongText',
    'getImage'
}
imageSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True)
imageSelect.add('Mickey', 'Minnie')

hideBoard = types.ReplyKeyboardRemove()

def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUser.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0

def listener(message):
    for m in message:
        if m.content_type == 'text':
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

bot = telebot.TeleBot(config.TOKEN)
bot.set_update_listener(listener)


@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if cid not in knownUser:
        knownUser.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, "Hello, stranger, let me scan you...")
        bot.send_message(cid, "Scanning complete, I know you now")
        command_help(m)
    else:
        bot.send_message(cid, "I already know you, no need for me to scan you again!")

@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    bot.send_message(cid, "Hello world")  # send the generated help page

@bot.message_handler(commands=['sendLongText'])
def command_long_text(m):
    cid = m.chat.id
    bot.send_message(cid, "If you think so....")
    bot.send_chat_action(cid, "typing")
    time.sleep(3)
    bot.send_message(cid, ".")

@bot.message_handler(commands=['getImage'])
def command_image(m):
    cid = m.chat.id
    bot.send_message(cid, "Please choose your image now", reply_markup=imageSelect)
    userStep[cid] = 1

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def msg_image_select(m):
    cid = m.chat.id
    text = m.text
    bot.send_chat_action(cid, "typing")
    if text == 'Mickey':  # send the appropriate image based on the reply to the "/getImage" command
        bot.send_photo(cid, open('rooster.jpg', 'rb'),
                       reply_markup=hideBoard)  # send file and hide keyboard, after image is sent
        userStep[cid] = 0  # reset the users step back to 0
    elif text == 'Minnie':
        bot.send_photo(cid, open('kitten.jpg', 'rb'), reply_markup=hideBoard)
        userStep[cid] = 0
    else:
        bot.send_message(cid, "Please, use the predefined keyboard!")
        bot.send_message(cid, "Please try again")

bot.polling()
from metar import Metar
import re
import requests
import json
import config
import telebot

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, 'Now send the ICAO code of the desired airport to get human-readable weather '
                                      'information.\nYou can find out code of your city airport here '
                                      '- http://www.rap.ucar.edu/weather/surface/stations.txt')

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    bot.send_message(message.chat.id, "Good bye!")

@bot.message_handler(commands=['ip'])
def handle_ip(message):
    link_ip = 'https://api.ipify.org?format=json'
    response_ip = requests.get(link_ip)
    try:
        parsed_response_ip = json.loads(response_ip.text)
        ip = parsed_response_ip["ip"]
    except ValueError as e:
        ip = 'An error has occurred. Please try again or contact the bot administrator - @no1_tx.'
    bot.send_message(message.chat.id, ip)

@bot.message_handler(content_types=['text'])
def send_decoded(message):
    try:
        buff = str(message.text)
        check = re.compile(r'^[A-Za-z\s]*$')
        if len(buff) == 4 and check.match(buff):
            code = buff
            print(f'Starting fetch data for {code}')
            fetch_and_decode_metar(code)
            bot.send_message(message.chat.id, 'city: ' + city + '\n' + decoded_data)
        else:
            bot.send_message(message.chat.id, "This is not ICAO code. Try again.")
    except UnicodeDecodeError:
        bot.send_message(message.chat.id, "This is not ICAO code. Try again.")

def fetch_and_decode_metar(code):
    global decoded_data
    global city
    city = 'None'
    link = 'http://metartaf.ru/' + code + '.json'
    print(f'Send request to {link}')
    response = requests.get(link)
    try:
        parsed_response = json.loads(response.text)
        city = parsed_response['name']
        print(f'Accepted data for {city}')
        metar_data = parsed_response['metar']
        print(f'METAR DATA: {metar_data}')
        metar_data = metar_data.split('\n')
        metar_data = metar_data[1]
        decoded_data = Metar.Metar(metar_data)
        print(f'DECODED DATA: {decoded_data}')
        decoded_data = str(decoded_data)
    except ValueError as e:
        print('Oops!')
        decoded_data = 'An error occurred while querying information from the METAR server. ' \
                       '(An empty response was received, or you provided the wrong ICAO code.) ' \
                       'Check the code, try again, or contact the bot administrator - @no1_tx.'

if __name__ == '__main__':
    bot.polling(none_stop=True)
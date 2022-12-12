from random import choice

import config
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

token = config.token
bot = telebot.TeleBot(token, parse_mode=None)


class Button:
    list_buttons = []
    currents = ['BTC', 'ETH', 'USDT', 'BNB', 'USDC', 'BUSD', 'XRP', 'DOGE', 'ADA', 'MATIC', 'DOT', 'DAI', 'WTRX', 'LTC',
                'SHIB', 'TRX', 'HEX', 'SOL', 'UNI', 'stETH', 'AVAX', 'LEO', 'LINK', 'WBTC', 'ATOM', 'XMR', 'ETC', 'TON',
                'XLM', 'BCH', 'ALGO', 'CRO', 'FIL', 'APE', 'QNT', 'NEAR', 'VET', 'OKB', 'ICP', 'HBAR', 'EOS', 'WBNB',
                'EGLD', 'TWT', 'FLOW', 'LUNC', 'FRAX', 'HT', 'USDP', 'CHZ']

    # currents = ['BTC', 'USDT', 'ETH', 'SHIB', 'DOGE', 'ADA', 'USDC']

    @classmethod
    def create_buttons(cls, val=None):
        markup = types.InlineKeyboardMarkup()
        for current in cls.currents:
            if current != val:
                cls.list_buttons.append(types.InlineKeyboardButton(current, callback_data=current))
        markup.add(*cls.list_buttons)
        return markup


class Pair:
    first_choice = False
    list_pair = []

    @classmethod
    def create_pair(cls, current):
        current = current.upper()
        cls.list_pair.append(current)
        return cls.list_pair


def get_graphic(message, par_valuts):
    pair = ''.join(par_valuts)
    timeframe = choice(['5m', '15m', '1h', '4h', '1d', '1w', '1M'])
    candles = choice([i for i in range(1, 1000, 100)])
    ma = choice([i for i in range(10, 100, 10)])
    tp = choice([i for i in range(10, 50, 10)])
    sl = choice([i for i in range(10, 50, 10)])

    data = {
        'pair': pair,
        'timeframe': timeframe,
        'candles': candles,
        'ma': ma,
        'tp': tp,
        'sl': sl,
    }
    try:
        res = requests.post('https://paper-trader.frwd.one', data=data)
        soup = BeautifulSoup(res.text, 'lxml')
        url_img = 'https://paper-trader.frwd.one' + soup.find('img')['src'].strip('.')
        return url_img
    except ConnectionError:
        bot.send_message(message.chat.id, 'Try again, press "/start"')


@bot.message_handler(commands=['start'])
def choice_pair(message, val=None):
    if val is None:
        markup = Button.create_buttons()
        bot.send_message(message.chat.id, 'Welcome to PaperTrader. Choose the first currency', reply_markup=markup)
    else:
        markup = Button.create_buttons(val)
        bot.send_message(message.chat.id, 'Choose a second currency', reply_markup=markup)
    return markup


def check_choice(item):
    return True if item.data.upper() in Button.currents else False


@bot.callback_query_handler(func=check_choice)
def callback_query(call):
    bot.answer_callback_query(call.id, call.data)
    if Pair.first_choice is False:
        Pair.create_pair(call.data)
        Button.list_buttons.clear()
        choice_pair(call.message, call.data)
        bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        Pair.first_choice = True
    else:
        Pair.create_pair(call.data)
        bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, f"Thank you. Your choice '{''.join(Pair.list_pair)}'")
        try:
            img_grafic = get_graphic(call.message, Pair.list_pair)
            bot.send_photo(call.message.chat.id, img_grafic)
        except TypeError:
            bot.send_message(call.message.chat.id,
                             "Sorry, pair does not support in the site. Choose another pair.Recommended pair 'BTCUSDT'")
        Button.list_buttons.clear()
        Pair.list_pair.clear()
        Pair.first_choice = False


bot.polling(none_stop=True)

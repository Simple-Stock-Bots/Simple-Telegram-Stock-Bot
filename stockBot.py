# Work with Python 3.6
import json
import logging
import re
import urllib.request

import telegram
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import credentials
import tickerInfo

TOKEN = credentials.secrets['TELEGRAM_TOKEN']

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""


news = {
    'Bravos': 'https://bravos.co/' + ticker,
    'Seeking Alpha': 'https://seekingalpha.com/symbol/' + ticker,
    'MSN Money': 'https://www.msn.com/en-us/money/stockdetails?symbol=' + ticker,
    'Yahoo Finance': 'https://finance.yahoo.com/quote/' + ticker,
    'Wall Street Journal': 'https://quotes.wsj.com/' + ticker,
    'The Street': 'https://www.thestreet.com/quote/' + ticker + '.html',
    'Zacks': 'https://www.zacks.com/stock/quote/' + ticker
}


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('I am started and ready to go!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text("I don't know how to help yet!")


def stockInfo(bot, update):
    message = update.message.text
    try:
        # regex to find tickers in messages, looks for up to 4 word characters following a dollar sign and captures the 4 word characters
        tickers = re.findall('[$](\w{1,4})', message)

        # get ticker information from bravos api, turns tickers into comma separated list so that only one api call is needed per message
        url = 'https://data.bravos.co/v1/quote?symbols=' + ",".join(tickers) + \
            '&apikey=' + BRAVOS_API + '&format=json'

        # load json data from url as an object
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())

            for ticker in tickers:  # iterate through the tickers and print relevant info one message at a time

                try:  # checks if data is a valid ticker, if it is not tells the user

                    # Get Stock ticker name from Data Object
                    nameTicker = data[ticker.upper()]['name']
                    # Get Stock Ticker price from Object
                    priceTicker = data[ticker.upper()]['price']

                    # Checks if !news is called, and prints news embed if it is
                    if message.startswith('!news'):
                        newsMessage = 'The current stock price of ' + \
                            nameTicker + ' is $**' + str(priceTicker) + '**'
                        for source in news:
                            print(source)
                            newsMessage = newsMessage + \
                                '\n [' + source + '](' + news[source] + ')'

                        update.message.reply_text(
                            text=newsMessage, parse_mode=telegram.ParseMode.MARKDOWN)
                    else:  # If news embed isnt called, print normal stock price
                        update.message.reply_text(
                            text='The current stock price of ' + nameTicker + ' is $**' + str(priceTicker) + '**', parse_mode=telegram.ParseMode.MARKDOWN)

                except KeyError:  # If searching for the ticker in loaded data fails, then Bravos didnt provide it, so tell the user.
                    update.message.reply_text(
                        ticker.upper() + ' does not exist.')
                    pass
    except:
        pass


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, stockInfo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

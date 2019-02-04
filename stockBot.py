# Work with Python 3.7
import json
import logging
import re
import urllib.request

import telegram
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import credentials
import tickerInfo

TOKEN = credentials.secrets["TELEGRAM_TOKEN"]

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
print("Bot Online")


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text("I am started and ready to go!")


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text("I don't know how to help yet!")


def stockInfo(bot, update):
    message = update.message.text
    chat_id = update.message.chat_id

    try:
        # regex to find tickers in messages, looks for up to 4 word characters following a dollar sign and captures the 4 word characters
        tickers = re.findall("[$](\w{1,4})", message)
        bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        # Checks if !news is called, and prints news embed if it is
        if message.startswith("!news"):
            tickerData = tickerInfo.tickerQuote(tickers)
            for ticker in tickers:
                ticker = ticker.upper()
                # bot.send_photo(bot.get_updates()
                #              [-1].message.chat_id, tickerData[ticker + 'Image'])
                name = tickerData[ticker + "Name"]
                price = tickerData[ticker + "Price"]
                change = tickerData[ticker + "Change"]

                message = (
                    "The current stock price of " + name + " is $**" + str(price) + "**"
                )
                if change > 0:
                    message = (
                        message + ", the stock is currently **up " + str(change) + "%**"
                    )
                elif change < 0:
                    message = (
                        message
                        + ", the stock is currently **down"
                        + str(change)
                        + "%**"
                    )
                else:
                    message = message + ", the stock hasn't shown any movement today."

                news = tickerInfo.stockNewsList(ticker)
                for source in news:
                    message = message + "\n[" + source + "](" + news[source] + ")"

                update.message.reply_text(
                    text=message, parse_mode=telegram.ParseMode.MARKDOWN
                )

        else:  # If news isnt called, print normal stock price
            tickerData = tickerInfo.tickerQuote(tickers)
            for ticker in tickers:
                ticker = ticker.upper()
                name = tickerData[ticker + "Name"]
                price = tickerData[ticker + "Price"]
                change = tickerData[ticker + "Change"]
                message = (
                    "The current stock price of " + name + " is $**" + str(price) + "**"
                )
                if change > 0:
                    message = (
                        message + ", the stock is currently **up " + str(change) + "%**"
                    )
                elif change < 0:
                    message = (
                        message
                        + ", the stock is currently **down "
                        + str(change)
                        + "%**"
                    )
                else:
                    message = message + ", the stock hasn't shown any movement today."
                update.message.reply_text(
                    text=message, parse_mode=telegram.ParseMode.MARKDOWN
                )
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


if __name__ == "__main__":
    main()

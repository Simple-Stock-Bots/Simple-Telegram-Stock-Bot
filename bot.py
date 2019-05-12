# Work with Python 3.7
import logging
import os

import telegram
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from functions import *

TOKEN = os.environ["TELEGRAM"]
TICKER_REGEX = "[$]([a-zA-Z]{1,4})"

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
    """Send link to docs when the command /help is issued."""
    message = "[Please see the docs for Bot information](https://misterbiggs.gitlab.io/simple-telegram-bot)"
    update.message.reply_text(text=message, parse_mode=telegram.ParseMode.MARKDOWN)


def tickerDetect(bot, update):
    """
    Runs on any message that doesn't have a command and searches for tickers, then returns the prices of any tickers found. 
    """
    message = update.message.text
    chat_id = update.message.chat_id

    # Let user know bot is working
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

    tickers = getTickers(message)

    data = tickerData(tickers) if tickers else {}

    for ticker in data:

        # Keep track of which tickers had a return from tickerData()
        if ticker.lower() in tickers:
            tickers.remove(ticker.lower())

        reply = tickerDataReply(data[ticker])
        update.message.reply_text(text=reply, parse_mode=telegram.ParseMode.MARKDOWN)

    # For any tickers that didnt have data, return that they don't exist.
    for ticker in tickers:
        update.message.reply_text(
            ticker.upper()
            + " does not exist, you should search for a real stock like $PSEC"
        )


def news(bot, update):
    """
    /news
    Returns a small snippet of general information, and any news articles that are found.
    """
    message = update.message.text
    chat_id = update.message.chat_id

    # Let user know bot is working
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

    tickers = getTickers(message)

    news = tickerNews(tickers) if tickers else {}

    for ticker in news:

        reply = tickerNewsReply(news[ticker])
        update.message.reply_text(text=reply, parse_mode=telegram.ParseMode.MARKDOWN)

        # Keep track of which tickers had a return from tickerData()
        if ticker.lower() in tickers:
            tickers.remove(ticker.lower())


def dividend(bot, update):
    """
    This Functions is incomplete.
    """
    message = update.message.text
    chat_id = update.message.chat_id

    # regex to find tickers in messages, looks for up to 4 word characters following a dollar sign and captures the 4 word characters
    tickers = re.findall(TICKER_REGEX, message)
    bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

    for ticker in tickers:
        message = tickerDividend(ticker)
        update.message.reply_text(text=message, parse_mode=telegram.ParseMode.MARKDOWN)


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
    dp.add_handler(CommandHandler("news", news))
    dp.add_handler(CommandHandler("dividend", dividend))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, tickerDetect))

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

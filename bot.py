# Works with Python 3.8
import logging
import os

import telegram
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

from functions import Symbol

TELEGRAM_TOKEN = os.environ["TELEGRAM"]
IEX_TOKEN = os.environ["IEX"]

s = Symbol(IEX_TOKEN)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
print("Bot Online")


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("I am started and ready to go!")


def help(update, context):
    """Send link to docs when the command /help is issued."""
    message = "[Please see the documentaion for Bot information](https://simple-stock-bots.gitlab.io/site/telegram/)"
    update.message.reply_text(text=message, parse_mode=telegram.ParseMode.MARKDOWN)


def symbol_detect(update, context):
    """
    Runs on any message that doesn't have a command and searches for symbols, then returns the prices of any symbols found. 
    """
    message = update.message.text
    chat_id = update.message.chat_id
    symbols = s.find_symbols(message)

    if symbols:
        # Let user know bot is working
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.price_reply(symbols).items():

            update.message.reply_text(
                text=reply[1], parse_mode=telegram.ParseMode.MARKDOWN
            )


def dividend(update, context):
    """
    waits for /dividend or /div command and then finds dividend info on that symbol.
    """
    message = update.message.text
    chat_id = update.message.chat_id
    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.dividend_reply(symbols).items():

            update.message.reply_text(
                text=reply[1], parse_mode=telegram.ParseMode.MARKDOWN
            )


def news(update, context):
    """
    waits for /news command and then finds news info on that symbol.
    """
    message = update.message.text
    chat_id = update.message.chat_id
    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.news_reply(symbols).items():
            update.message.reply_text(
                text=reply[1], parse_mode=telegram.ParseMode.MARKDOWN
            )


def info(update, context):
    """
    waits for /info command and then finds info on that symbol.
    """
    message = update.message.text
    chat_id = update.message.chat_id
    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.info_reply(symbols).items():
            update.message.reply_text(
                text=reply[1], parse_mode=telegram.ParseMode.MARKDOWN
            )


def inline_query(update, context):
    """
    Handles inline query.
    Does a fuzzy search on input and returns stocks that are close.
    """
    print(update.inline_query.query)
    matches = s.search_symbols(update.inline_query.query)
    results = []
    for match in matches:
        try:
            price = s.price_reply([match[0]])[match[0]]
            results.append(
                InlineQueryResultArticle(
                    match[0],
                    title=match[1],
                    input_message_content=InputTextMessageContent(
                        price, parse_mode=telegram.ParseMode.MARKDOWN
                    ),
                )
            )
        except TypeError:
            logging.warning(str(match))
            pass

        if len(results) == 5:
            update.inline_query.answer(results)
            return


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the context.bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("dividend", dividend))
    dp.add_handler(CommandHandler("div", dividend))
    dp.add_handler(CommandHandler("news", news))
    dp.add_handler(CommandHandler("info", info))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, symbol_detect))

    # Inline Bot commands
    dp.add_handler(InlineQueryHandler(inline_query))

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

# Works with Python 3.8
import datetime
import io
import logging
import os
import random
import html
import json
import traceback

import mplfinance as mpf
import telegram
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    LabeledPrice,
    Update,
)
from telegram.ext import (
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    Updater,
    CallbackContext,
)

from IEX_Symbol import IEX_Symbol
from cg_Crypto import cg_Crypto
from T_info import T_info

TELEGRAM_TOKEN = os.environ["TELEGRAM"]

try:
    IEX_TOKEN = os.environ["IEX"]
except KeyError:
    IEX_TOKEN = ""
    print("Starting without an IEX Token will not allow you to get market data!")
try:
    STRIPE_TOKEN = os.environ["STRIPE"]
except KeyError:
    STRIPE_TOKEN = ""
    print("Starting without a STRIPE Token will not allow you to accept Donations!")

s = IEX_Symbol(IEX_TOKEN)
c = cg_Crypto()
t = T_info()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
print("Bot Online")


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(text=t.help_text, parse_mode=telegram.ParseMode.MARKDOWN)


def help(update: Update, context: CallbackContext):
    """Send link to docs when the command /help is issued."""

    update.message.reply_text(text=t.help_text, parse_mode=telegram.ParseMode.MARKDOWN)


def license(update: Update, context: CallbackContext):
    """Return bots license agreement"""

    update.message.reply_text(text=t.license, parse_mode=telegram.ParseMode.MARKDOWN)


def status(update: Update, context: CallbackContext):
    message = ""
    try:
        # Bot Status
        bot_resp = (
            datetime.datetime.now(update.message.date.tzinfo) - update.message.date
        )
        message += f"It took {bot_resp.total_seconds()} seconds for the bot to get your message.\n"

        # IEX Status
        message += s.iex_status() + "\n"

        # Message Status
        message += s.message_status()
    except Exception as ex:
        message += (
            f"*\n\nERROR ENCOUNTERED:*\n{ex}\n\n"
            + "*The bot encountered an error while attempting to find errors. Please contact the bot admin.*"
        )

    update.message.reply_text(text=message, parse_mode=telegram.ParseMode.MARKDOWN)


def donate(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    if update.message.text.strip() == "/donate":
        update.message.reply_text(
            text=t.donate_text, parse_mode=telegram.ParseMode.MARKDOWN
        )
        return
    else:
        amount = update.message.text.replace("/donate", "").replace("$", "").strip()
    title = "Simple Stock Bot Donation"
    description = f"Simple Stock Bot Donation of ${amount}"
    payload = "simple-stock-bot"
    provider_token = STRIPE_TOKEN
    start_parameter = str(chat_id)

    print(start_parameter)
    currency = "USD"

    try:
        price = int(float(amount) * 100)
    except ValueError:
        update.message.reply_text(f"{amount} is not a valid donation amount or number.")
        return
    print(price)

    prices = [LabeledPrice("Donation:", price)]

    context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        start_parameter,
        currency,
        prices,
    )


def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query

    if query.invoice_payload == "simple-stock-bot":
        # answer False pre_checkout_query
        query.answer(ok=True)
    else:
        query.answer(ok=False, error_message="Something went wrong...")


def successful_payment_callback(update: Update, context: CallbackContext):
    update.message.reply_text("Thank you for your donation!")


def symbol_detect(update: Update, context: CallbackContext):
    """
    Runs on any message that doesn't have a command and searches for symbols,
        then returns the prices of any symbols found.
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


def dividend(update: Update, context: CallbackContext):
    """
    waits for /dividend or /div command and then finds dividend info on that symbol.
    """
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip() == "/dividend":
        update.message.reply_text(
            "This command gives info on the next dividend date for a symbol.\nExample: /dividend $tsla"
        )
        return

    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        for symbol in symbols:
            update.message.reply_text(
                text=s.dividend_reply(symbol), parse_mode=telegram.ParseMode.MARKDOWN
            )


def news(update: Update, context: CallbackContext):
    """
    waits for /news command and then finds news info on that symbol.
    """
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip() == "/news":
        update.message.reply_text(
            "This command gives the most recent english news for a symbol.\nExample: /news $tsla"
        )
        return

    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.news_reply(symbols).items():
            update.message.reply_text(
                text=reply[1], parse_mode=telegram.ParseMode.MARKDOWN
            )


def info(update: Update, context: CallbackContext):
    """
    waits for /info command and then finds info on that symbol.
    """
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip() == "/info":
        update.message.reply_text(
            "This command gives information on a symbol.\nExample: /info $tsla"
        )
        return

    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.info_reply(symbols).items():
            update.message.reply_text(
                text=reply[1], parse_mode=telegram.ParseMode.MARKDOWN
            )


def search(update: Update, context: CallbackContext):
    message = update.message.text.replace("/search ", "")
    chat_id = update.message.chat_id

    if message.strip() == "/search":
        update.message.reply_text(
            "This command searches for symbols supported by the bot.\nExample: /search Tesla Motors or /search $tsla"
        )
        return

    context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    queries = s.search_symbols(message)[:6]
    if queries:
        reply = "*Search Results:*\n`$ticker: Company Name`\n"
        for query in queries:
            reply += "`" + query[1] + "`\n"
        update.message.reply_text(text=reply, parse_mode=telegram.ParseMode.MARKDOWN)


def intra(update: Update, context: CallbackContext):
    # TODO: Document usage of this command. https://iexcloud.io/docs/api/#historical-prices

    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip() == "/intra":
        update.message.reply_text(
            "This command returns a chart of the stocks movement since the most recent market open.\nExample: /intra $tsla"
        )
        return

    symbol = s.find_symbols(message)[0]

    df = s.intra_reply(symbol)
    if df.empty:
        update.message.reply_text(
            text="Invalid symbol please see `/help` for usage details.",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        return

    context.bot.send_chat_action(
        chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO
    )

    buf = io.BytesIO()
    mpf.plot(
        df,
        type="renko",
        title=f"\n${symbol.upper()}",
        volume=True,
        style="yahoo",
        mav=20,
        savefig=dict(fname=buf, dpi=400, bbox_inches="tight"),
    )
    buf.seek(0)

    update.message.reply_photo(
        photo=buf,
        caption=f"\nIntraday chart for ${symbol.upper()} from {df.first_valid_index().strftime('%I:%M')} to"
        + f" {df.last_valid_index().strftime('%I:%M')} ET on"
        + f" {datetime.date.today().strftime('%d, %b %Y')}\n\n{s.price_reply([symbol])[symbol]}",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def chart(update: Update, context: CallbackContext):
    # TODO: Document usage of this command. https://iexcloud.io/docs/api/#historical-prices

    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip() == "/chart":
        update.message.reply_text(
            "This command returns a chart of the stocks movement for the past month.\nExample: /chart $tsla"
        )
        return

    symbol = s.find_symbols(message)[0]

    df = s.chart_reply(symbol)
    if df.empty:
        update.message.reply_text(
            text="Invalid symbol please see `/help` for usage details.",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        return

    context.bot.send_chat_action(
        chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO
    )

    buf = io.BytesIO()
    mpf.plot(
        df,
        type="candle",
        title=f"\n${symbol.upper()}",
        volume=True,
        style="yahoo",
        savefig=dict(fname=buf, dpi=400, bbox_inches="tight"),
    )
    buf.seek(0)

    update.message.reply_photo(
        photo=buf,
        caption=f"\n1 Month chart for ${symbol.upper()} from {df.first_valid_index().strftime('%d, %b %Y')}"
        + f" to {df.last_valid_index().strftime('%d, %b %Y')}\n\n{s.price_reply([symbol])[symbol]}",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def stat(update: Update, context: CallbackContext):
    """
    https://iexcloud.io/docs/api/#key-stats
    """
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip() == "/stat":
        update.message.reply_text(
            "This command returns key statistics for a symbol.\nExample: /stat $tsla"
        )
        return

    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.stat_reply(symbols).items():
            update.message.reply_text(
                text=reply[1], parse_mode=telegram.ParseMode.MARKDOWN
            )


def crypto(update: Update, context: CallbackContext):
    """
    https://iexcloud.io/docs/api/#cryptocurrency-quote
    """
    context.bot.send_chat_action(
        chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING
    )
    message = update.message.text

    if message.strip() == "/crypto":
        update.message.reply_text(
            "This command returns the current price in USD for a cryptocurrency.\nExample: /crypto eth"
        )
        return

    reply = s.crypto_reply(message)

    if reply:
        update.message.reply_text(text=reply, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        update.message.reply_text(
            text=f"Pair: {message} returned an error.",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )


def inline_query(update: Update, context: CallbackContext):
    """
    Handles inline query.
    Does a fuzzy search on input and returns stocks that are close.
    """

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


def rand_pick(update: Update, context: CallbackContext):

    choice = random.choice(list(s.symbol_list["description"]))
    hold = (
        datetime.date.today() + datetime.timedelta(random.randint(1, 365))
    ).strftime("%b %d, %Y")

    update.message.reply_text(
        text=f"{choice}\nBuy and hold until: {hold}",
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
    update.message.reply_text(text="Please inform the bot admin of this issue.")


def main():
    """Start the context.bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("license", license))
    dp.add_handler(CommandHandler("dividend", dividend))
    dp.add_handler(CommandHandler("div", dividend))
    dp.add_handler(CommandHandler("news", news))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("stat", stat))
    dp.add_handler(CommandHandler("stats", stat))
    dp.add_handler(CommandHandler("search", search))
    dp.add_handler(CommandHandler("intraday", intra))
    dp.add_handler(CommandHandler("intra", intra, run_async=True))
    dp.add_handler(CommandHandler("chart", chart))
    dp.add_handler(CommandHandler("crypto", crypto))
    dp.add_handler(CommandHandler("random", rand_pick))
    dp.add_handler(CommandHandler("donate", donate))
    dp.add_handler(CommandHandler("status", status))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, symbol_detect))

    # Inline Bot commands
    dp.add_handler(InlineQueryHandler(inline_query))

    # Pre-checkout handler to final check
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Payment success
    dp.add_handler(
        MessageHandler(Filters.successful_payment, successful_payment_callback)
    )

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

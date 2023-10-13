# Works with Python 3.8
import datetime
import html
import io
import json
import logging
import os
import random
import string
import traceback
from uuid import uuid4

import mplfinance as mpf
import telegram
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    LabeledPrice,
    Update,
)

from telegram.ext import (
    Application,
    CommandHandler,
    InlineQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from common.symbol_router import Router
from T_info import T_info

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM"]

try:
    STRIPE_TOKEN = os.environ["STRIPE"]
except KeyError:
    STRIPE_TOKEN = ""
    log.warning("Starting without a STRIPE Token will not allow you to accept Donations!")

s = Router()
t = T_info()


log.info("Bot script started.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help text when the command /start is issued."""
    log.info(f"Start command ran by {update.message.chat.username}")
    await update.message.reply_text(
        text=t.help_text,
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_notification=True,
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help text when the command /help is issued."""
    log.info(f"Help command ran by {update.message.chat.username}")
    await update.message.reply_text(
        text=t.help_text,
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_notification=True,
    )


async def license(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send bots license when the /license command is issued."""
    log.info(f"License command ran by {update.message.chat.username}")
    await update.message.reply_text(
        text=t.license,
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_notification=True,
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gather status of bot and dependant services and return important status updates."""
    log.warning(f"Status command ran by {update.message.chat.username}")
    bot_resp_time = datetime.datetime.now(update.message.date.tzinfo) - update.message.date

    bot_status = s.status(f"It took {bot_resp_time.total_seconds()} seconds for the bot to get your message.")

    await update.message.reply_text(
        text=bot_status,
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
    )


async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets up donation."""
    log.info(f"Donate command ran by {update.message.chat.username}")
    chat_id = update.message.chat_id

    if update.message.text.strip() == "/donate" or "/donate@" in update.message.text:
        await update.message.reply_text(
            text=t.donate_text,
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            disable_notification=True,
        )
        amount = 1.0
    else:
        amount = float(update.message.text.replace("/donate", "").replace("$", "").strip())

    try:
        price = int(amount * 100)
    except ValueError:
        await update.message.reply_text(f"{amount} is not a valid donation amount or number.")
        return
    log.info(f"Donation amount: {price} by {update.message.chat.username}")

    await context.bot.send_invoice(
        chat_id=chat_id,
        title="Simple Stock Bot Donation",
        description=f"Simple Stock Bot Donation of ${amount} by {update.message.chat.username}",
        payload=f"simple-stock-bot-{chat_id}",
        provider_token=STRIPE_TOKEN,
        currency="USD",
        prices=[LabeledPrice("Donation:", price)],
        start_parameter="",
        # suggested_tip_amounts=[100, 500, 1000, 2000],
        photo_url="https://simple-stock-bots.gitlab.io/docs/img/Telegram.png",
        photo_width=500,
        photo_height=500,
    )


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approves donation"""
    log.info("precheckout_callback queried")
    query = update.pre_checkout_query

    await query.answer(ok=True)
    # I dont think I need to check since its only donations.
    # if query.invoice_payload == "simple-stock-bot":
    #     # answer False pre_checkout_query
    #     await query.answer(ok=True)
    # else:
    #     await query.answer(ok=False, error_message="Something went wrong...")


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Thanks user for donation"""
    log.info("Successful payment!")
    await update.message.reply_text("Thank you for your donation! It goes a long way to keeping the bot free!")


async def symbol_detect_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Makes image captions into text then passes the `update` and `context`
        to symbol detect so that it can reply cashtags in image captions.
    """
    try:
        if update.message.caption:
            update.message.text = update.message.caption
            await symbol_detect(update, context)
    except AttributeError:
        return


async def symbol_detect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs on any message that doesn't have a command and searches for cashtags,
        then returns the prices of any symbols found.
    """
    try:
        message = update.message.text
        chat_id = update.message.chat_id
        if "$" in message:
            log.info("Looking for Symbols")
            symbols = s.find_symbols(message)
        else:
            return
    except AttributeError as ex:
        log.info(ex)
        return

    # Detect Options
    if ("call" in message.lower()) or ("put" in message.lower()):
        log.info("Options detected")
        await context.bot.send_chat_action(chat_id=chat_id, action=telegram.constants.ChatAction.TYPING)
        try:
            options_data = s.options(message, symbols)

            await update.message.reply_text(
                text=generate_options_reply(options_data),
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
            )
            return
        except KeyError as ex:
            logging.warning(ex)
            pass

    if symbols:
        log.info(f"Symbols found: {symbols}")
        await context.bot.send_chat_action(chat_id=chat_id, action=telegram.constants.ChatAction.TYPING)

        for reply in s.price_reply(symbols):
            await update.message.reply_text(
                text=reply,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                disable_notification=True,
            )


def generate_options_reply(options_data: dict):
    # Header with Option Symbol and Underlying
    message_text = f"*{options_data['Option Symbol']} ({options_data['Underlying']})*\n\n"

    # Key details
    details = (
        f"*Expiration:* `{options_data['Expiration']}`\n"
        f"*Side:* `{options_data['side']}`\n"
        f"*Strike:* `{options_data['strike']}`\n"
        f"*First Traded:* `{options_data['First Traded']}`\n"
        f"*Last Updated:* `{options_data['Last Updated']}`\n\n"
    )
    message_text += details

    # Pricing info
    pricing_info = (
        f"*Bid:* `{options_data['bid']}` (Size: `{options_data['bidSize']}`)\n"
        f"*Mid:* `{options_data['mid']}`\n"
        f"*Ask:* `{options_data['ask']}` (Size: `{options_data['askSize']}`)\n"
        f"*Last:* `{options_data['last']}`\n\n"
    )
    message_text += pricing_info

    # Volume and open interest
    volume_info = f"*Open Interest:* `{options_data['Open Interest']}`\n" f"*Volume:* `{options_data['Volume']}`\n\n"
    message_text += volume_info

    # Greeks
    greeks_info = (
        f"*IV:* `{options_data['Implied Volatility']}`\n"
        f"*Delta:* `{options_data['delta']}`\n"
        f"*Gamma:* `{options_data['gamma']}`\n"
        f"*Theta:* `{options_data['theta']}`\n"
        f"*Vega:* `{options_data['vega']}`\n"
        f"*Rho:* `{options_data['rho']}`\n"
    )
    message_text += greeks_info

    return message_text


async def intra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """returns a chart of intraday data for a symbol"""
    log.info(f"Intra command ran by {update.message.chat.username}")

    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/intra":
        await update.message.reply_text(
            "This command returns a chart of the stocks movement since the most recent market open.\nExample: /intra $tsla"
        )
        return

    symbols = s.find_symbols(message, trending_weight=5)
    symbol = symbols[0]

    if len(symbols):
        symbol = symbols[0]
    else:
        await update.message.reply_text("No symbols or coins found.")
        return

    df = s.intra_reply(symbol)
    if df.empty:
        await update.message.reply_text(
            text="Invalid symbol please see `/help` for usage details.",
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            disable_notification=True,
        )
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=telegram.constants.ChatAction.UPLOAD_PHOTO)

    buf = io.BytesIO()
    mpf.plot(
        df,
        type="renko",
        title=f"\n{symbol.name}",
        volume="Volume" in df.keys(),
        style="yahoo",
        savefig=dict(fname=buf, dpi=400, bbox_inches="tight"),
    )
    buf.seek(0)

    await update.message.reply_photo(
        photo=buf,
        caption=f"\nIntraday chart for {symbol.name} from {df.first_valid_index().strftime('%d %b at %H:%M')} to"
        + f" {df.last_valid_index().strftime('%d %b at %H:%M %Z')}"
        + f"\n\n{s.price_reply([symbol])[0]}",
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_notification=True,
    )


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """returns a chart of the past month of data for a symbol"""
    log.info(f"Chart command ran by {update.message.chat.username}")

    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/chart":
        await update.message.reply_text(
            "This command returns a chart of the stocks movement for the past month.\nExample: /chart $tsla"
        )
        return

    symbols = s.find_symbols(message, trending_weight=10)

    if len(symbols):
        symbol = symbols[0]
    else:
        await update.message.reply_text("No symbols or coins found.")
        return

    df = s.chart_reply(symbol)
    if df.empty:
        await update.message.reply_text(
            text="Invalid symbol please see `/help` for usage details.",
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            disable_notification=True,
        )
        return
    await context.bot.send_chat_action(chat_id=chat_id, action=telegram.constants.ChatAction.UPLOAD_PHOTO)

    buf = io.BytesIO()
    mpf.plot(
        df,
        type="candle",
        title=f"\n{symbol.name}",
        volume="Volume" in df.keys(),
        style="yahoo",
        savefig=dict(fname=buf, dpi=400, bbox_inches="tight"),
    )
    buf.seek(0)

    await update.message.reply_photo(
        photo=buf,
        caption=f"\n1 Month chart for {symbol.name} from {df.first_valid_index().strftime('%d, %b %Y')}"
        + f" to {df.last_valid_index().strftime('%d, %b %Y')}\n\n{s.price_reply([symbol])[0]}",
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_notification=True,
    )


async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """returns currently trending symbols and how much they've moved in the past trading day."""
    log.info(f"Trending command ran by {update.message.chat.username}")

    chat_id = update.message.chat_id

    await context.bot.send_chat_action(chat_id=chat_id, action=telegram.constants.ChatAction.TYPING)

    trending_list = s.trending()

    await update.message.reply_text(
        text=trending_list,
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_notification=True,
    )


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles inline query. Searches by looking if query is contained
        in the symbol and returns matches in alphabetical order.
    """

    if not update.inline_query.query:
        return

    print(f"Query: {update.inline_query.query}")

    ignored_queries = {"$", "$$", " ", ""}

    if update.inline_query.query.strip() in ignored_queries:
        default_message = """
        You can type:\n@SimpleStockBot `[search]`
        in any chat or direct message to search for the stock bots full list of stock and crypto symbols and return the price.
        """

        await update.inline_query.answer(
            [
                InlineQueryResultArticle(
                    str(uuid4()),
                    title="Please enter a query. It can be a ticker or a name of a company.",
                    input_message_content=InputTextMessageContent(
                        default_message, parse_mode=telegram.constants.ParseMode.MARKDOWN
                    ),
                )
            ]
        )

    matches = s.inline_search(update.inline_query.query)

    results = []
    for _, row in matches.iterrows():
        results.append(
            InlineQueryResultArticle(
                str(uuid4()),
                title=row["description"],
                input_message_content=InputTextMessageContent(
                    row["price_reply"], parse_mode=telegram.constants.ParseMode.MARKDOWN
                ),
            )
        )

        if len(results) == 5:
            await update.inline_query.answer(results, cache_time=60 * 60)
            log.info("Inline Command was successful")
            return
    await update.inline_query.answer(results)


async def rand_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """For the gamblers. Returns a random symbol to buy and a sell date"""
    log.info(f"Someone is gambling! Random_pick command ran by {update.message.chat.username}")

    await update.message.reply_text(
        text=s.random_pick(),
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_notification=True,
    )


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    log.warning('Update "%s" caused error "%s"', update, error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    err_code = "".join([random.choice(string.ascii_lowercase) for i in range(5)])
    log.warning(f"Logging error: {err_code}")

    if update:
        log.warning(
            f"An exception was raised while handling an update\n"
            f"\tupdate = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}\n"
            f"\tcontext.chat_data = {str(context.chat_data)}\n"
            f"\tcontext.user_data = {str(context.user_data)}\n"
            f"\t{html.escape(tb_string)}"
        )

        await update.message.reply_text(
            text=f"An error has occured. Please inform @MisterBiggs if the error persists. Error Code: `{err_code}`",
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
        )
    else:
        log.warning("No message to send to user.")
        log.warning(tb_string)


def main():
    """Start the context.bot."""
    # Create the EventHandler and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("license", license))
    application.add_handler(CommandHandler("trending", trending))
    application.add_handler(CommandHandler("random", rand_pick))
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("inline", inline_query))

    # Charting can be slow so they run async.
    application.add_handler(CommandHandler("intra", intra, block=False))
    application.add_handler(CommandHandler("intraday", intra, block=False))
    application.add_handler(CommandHandler("day", intra, block=False))
    application.add_handler(CommandHandler("chart", chart, block=False))
    application.add_handler(CommandHandler("month", chart, block=False))

    # on noncommand i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT, symbol_detect))
    application.add_handler(MessageHandler(filters.PHOTO, symbol_detect_image))

    # Inline Bot commands
    application.add_handler(InlineQueryHandler(inline_query))

    # Pre-checkout handler to final check
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Payment success
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # log all errors
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

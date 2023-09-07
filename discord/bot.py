import datetime
import io
import logging
import os

import mplfinance as mpf
import nextcord
from nextcord.ext import commands

from D_info import D_info
from common.symbol_router import Router

DISCORD_TOKEN = os.environ["DISCORD"]

s = Router()
d = D_info()


intents = nextcord.Intents.default()


client = nextcord.Client(intents=intents)
bot = commands.Bot(command_prefix="/", description=d.help_text, intents=intents)

logger = logging.getLogger("nextcord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="nextcord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)


@bot.event
async def on_ready():
    logging.info("Starting Simple Stock Bot")
    logging.info(f"Logged in as {bot.user.name} {bot.user.id}")


@bot.command()
async def status(ctx: commands):
    """Debug command for diagnosing if the bot is experiencing any issues."""
    logging.warning(f"Status command ran by {ctx.message.author}")
    message = ""
    try:
        message = "Contact MisterBiggs#0465 if you need help.\n"
        message += s.status(f"Bot recieved your message in: {bot.latency*10:.4f} seconds") + "\n"

    except Exception as ex:
        logging.critical(ex)
        message += (
            f"*\n\nERROR ENCOUNTERED:*\n{ex}\n\n"
            + "*The bot encountered an error while attempting to find errors. Please contact the bot admin.*"
        )
    await ctx.send(message)


@bot.command()
async def license(ctx: commands):
    """Returns the bots license agreement."""
    await ctx.send(d.license)


@bot.command()
async def donate(ctx: commands):
    """Details on how to support the development and hosting of the bot."""
    await ctx.send(d.donate_text)


@bot.command()
async def search(ctx: commands, *, query: str):
    """Search for a stock symbol using either symbol of company name."""
    results = s.search_symbols(query)
    if results:
        reply = "*Search Results:*\n`$ticker: Company Name`\n"
        for query in results:
            reply += "`" + query[1] + "`\n"
        await ctx.send(reply)


@bot.command()
async def crypto(ctx: commands, _: str):
    """Get the price of a cryptocurrency using in USD."""
    await ctx.send("Crypto now has native support. Any crypto can be called using two dollar signs: `$$eth` `$$btc` `$$doge`")


@bot.command()
async def intra(ctx: commands, sym: str):
    """Get a chart for the stocks movement since market open."""
    symbols = s.find_symbols(sym)

    if len(symbols):
        symbol = symbols[0]
    else:
        await ctx.send("No symbols or coins found.")
        return

    df = s.intra_reply(symbol)
    if df.empty:
        await ctx.send("Invalid symbol please see `/help` for usage details.")
        return
    with ctx.channel.typing():
        buf = io.BytesIO()
        mpf.plot(
            df,
            type="renko",
            title=f"\n{symbol.name}",
            volume="volume" in df.keys(),
            style="yahoo",
            savefig=dict(fname=buf, dpi=400, bbox_inches="tight"),
        )

        buf.seek(0)

        # Get price so theres no request lag after the image is sent
        price_reply = s.price_reply([symbol])[0]
        await ctx.send(
            file=nextcord.File(
                buf,
                filename=f"{symbol.name}:intra{datetime.date.today().strftime('%S%M%d%b%Y')}.png",
            ),
            content=f"\nIntraday chart for {symbol.name} from {df.first_valid_index().strftime('%d %b at %H:%M')} to"
            + f" {df.last_valid_index().strftime('%d %b at %H:%M')}",
        )
        await ctx.send(price_reply)


@bot.command()
async def chart(ctx: commands, sym: str):
    """returns a chart of the past month of data for a symbol"""

    symbols = s.find_symbols(sym)

    if len(symbols):
        symbol = symbols[0]
    else:
        await ctx.send("No symbols or coins found.")
        return

    df = s.chart_reply(symbol)
    if df.empty:
        await ctx.send("Invalid symbol please see `/help` for usage details.")
        return
    with ctx.channel.typing():
        buf = io.BytesIO()
        mpf.plot(
            df,
            type="candle",
            title=f"\n{symbol.name}",
            volume="volume" in df.keys(),
            style="yahoo",
            savefig=dict(fname=buf, dpi=400, bbox_inches="tight"),
        )
        buf.seek(0)

        # Get price so theres no request lag after the image is sent
        price_reply = s.price_reply([symbol])[0]
        await ctx.send(
            file=nextcord.File(
                buf,
                filename=f"{symbol.name}:1M{datetime.date.today().strftime('%d%b%Y')}.png",
            ),
            content=f"\n1 Month chart for {symbol.name} from {df.first_valid_index().strftime('%d, %b %Y')}"
            + f" to {df.last_valid_index().strftime('%d, %b %Y')}",
        )
        await ctx.send(price_reply)


@bot.command()
async def cap(ctx: commands, sym: str):
    """Get the market cap of a symbol"""
    symbols = s.find_symbols(sym)
    if symbols:
        with ctx.channel.typing():
            for reply in s.cap_reply(symbols):
                await ctx.send(reply)


@bot.command()
async def trending(ctx: commands):
    """Get a list of Trending Stocks and Coins"""
    with ctx.channel.typing():
        await ctx.send(s.trending())


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    if message.content:
        if message.content[0] == "/":
            await bot.process_commands(message)
            return

        if "$" in message.content:
            symbols = s.find_symbols(message.content)

            if symbols:
                for reply in s.price_reply(symbols):
                    await message.channel.send(reply)
                return


bot.run(DISCORD_TOKEN)

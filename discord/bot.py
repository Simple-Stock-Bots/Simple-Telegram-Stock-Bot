import datetime
import io
import logging
import os

import mplfinance as mpf
import nextcord
from D_info import D_info
from nextcord.ext import commands

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
    logging.info(f"Status command ran by {ctx.message.author}")
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
    # Ignore messages from the bot itself
    if message.author.id == bot.user.id:
        return

    content_lower = message.content.lower()

    # Process commands starting with "/"
    if message.content.startswith("/"):
        await bot.process_commands(message)
        return

    symbols = None
    if "$" in message.content:
        symbols = s.find_symbols(message.content)

    if "call" in content_lower or "put" in content_lower:
        await handle_options(message, symbols)
        return

    if symbols:
        for reply in s.price_reply(symbols):
            await message.channel.send(reply)
        return


async def handle_options(message, symbols):
    logging.info("Options detected")
    try:
        options_data = s.options(message.content.lower(), symbols)

        # Create the embed directly within the function
        embed = nextcord.Embed(title=options_data["Option Symbol"], description=options_data["Underlying"], color=0x3498DB)

        # Key details
        details = (
            f"Expiration: {options_data['Expiration']}\n" f"Side: {options_data['side']}\n" f"Strike: {options_data['strike']}"
        )
        embed.add_field(name="Details", value=details, inline=False)

        # Pricing info
        pricing_info = (
            f"Bid: {options_data['bid']} (Size: {options_data['bidSize']})\n"
            f"Mid: {options_data['mid']}\n"
            f"Ask: {options_data['ask']} (Size: {options_data['askSize']})\n"
            f"Last: {options_data['last']}"
        )
        embed.add_field(name="Pricing", value=pricing_info, inline=False)

        # Volume and open interest
        volume_info = f"Open Interest: {options_data['Open Interest']}\n" f"Volume: {options_data['Volume']}"
        embed.add_field(name="Activity", value=volume_info, inline=False)

        # Greeks
        greeks_info = (
            f"IV: {options_data['Implied Volatility']}\n"
            f"Delta: {options_data['delta']}\n"
            f"Gamma: {options_data['gamma']}\n"
            f"Theta: {options_data['theta']}\n"
            f"Vega: {options_data['vega']}\n"
            f"Rho: {options_data['rho']}"
        )
        embed.add_field(name="Greeks", value=greeks_info, inline=False)

        # Send the created embed
        await message.channel.send(embed=embed)

    except KeyError as ex:
        logging.warning(f"KeyError processing options for message {message.content}: {ex}")


bot.run(DISCORD_TOKEN)

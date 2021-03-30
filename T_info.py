"""Functions and Info specific to the Telegram Bot
"""

import re
import requests as r


class T_info:
    license = re.sub(
        r"\b\n",
        " ",
        r.get(
            "https://gitlab.com/simple-stock-bots/simple-telegram-stock-bot/-/raw/master/LICENSE"
        ).text,
    )

    help_text = """
Thanks for using this bot, consider supporting it by [buying me a beer.](https://www.buymeacoffee.com/Anson)

Keep up with the latest news for the bot in its Telegram Channel: https://t.me/simplestockbotnews

Full documentation on using and running your own stock bot can be found [on the bots website.](https://simple-stock-bots.gitlab.io/site)

The bot detects _"Symbols"_ using either one or two dollar signs before the symbol. One dollar sign is for a stock market ticker, while two is for a cryptocurrency coin. `/chart $$eth` would return a chart of the past month of data for Ethereum, while `/dividend $psec` returns dividend information for Prospect Capital stock.

Simply calling a symbol in any message that the bot can see will also return the price. So a message like: `I wonder if $$btc will go to the Moon now that $tsla accepts it as payment` would return the current price for both Bitcoin and Tesla. 

**Commands**
        - `/donate [amount in USD]` to donate. 🎗️
        - `/dividend $[symbol]` Dividend information for the symbol. 📅
        - `/intra $[symbol]` Plot of the stocks movement since the last market open.  📈
        - `/chart $[symbol]` Plot of the stocks movement for the past 1 month. 📊
        - `/news $[symbol]` News about the symbol. 📰
        - `/info $[symbol]` General information about the symbol. ℹ️
        - `/stat $[symbol]` Key statistics about the symbol. 🔢
        - `/trending` Trending Stocks and Cryptos. 💬
        - `/help` Get some help using the bot. 🆘

**Inline Features**
    You can type @SimpleStockBot `[search]` in any chat or direct message to search for the stock bots full list of stock symbols and return the price of the ticker. Then once you select the ticker want the bot will send a message as you in that chat with the latest stock price.
    
    Market data is provided by [IEX Cloud](https://iexcloud.io)

    If you believe the bot is not behaving properly run `/status`.
    """

    donate_text = """
Simple Stock Bot is run entirely on donations[.](https://www.buymeacoffee.com/Anson)
All donations go directly towards paying for servers, and market data is provided by
[IEX Cloud](https://iexcloud.io/).

The easiest way to donate is to run the `/donate [amount in USD]` command with US dollars you would like to donate.

Example: `/donate 2` would donate 2 USD.
An alternative way to donate is through https://www.buymeacoffee.com/Anson,which accepts Paypal or Credit card.
If you have any questions get in touch: @MisterBiggs or [anson@ansonbiggs.com](http://mailto:anson@ansonbiggs.com/)

_Donations can only be made in a chat directly with @simplestockbot_
    """


commands = """
donate - Donate to the bot 🎗️
help - Get some help using the bot. 🆘
info - $[symbol] General information about the symbol. ℹ️
news - $[symbol] News about the symbol. 📰
stat - $[symbol] Key statistics about the symbol. 🔢
dividend - $[symbol] Dividend info 📅
intra - $[symbol] Plot since the last market open. 📈
trending - Trending Stocks and Cryptos. 💬
chart - $[chart] Plot of the past month. 📊
"""  # Not used by the bot but for updaing commands with BotFather

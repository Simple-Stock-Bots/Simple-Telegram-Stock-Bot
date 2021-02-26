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

Keep up with the latest news for the bot in itsTelegram Channel: https://t.me/simplestockbotnews

Full documentation on using and running your own stock bot can be found [here.](https://simple-stock-bots.gitlab.io/site)

**Commands**
        - /donate [amount in USD] to donate. 🎗️
        - /dividend $[symbol] will return dividend information for the symbol. 📅
        - /intra $[symbol] Plot of the stocks movement since the last market open.  📈
        - /chart $[symbol] Plot of the stocks movement for the past 1 month. 📊
        - /news $[symbol] News about the symbol. 📰
        - /info $[symbol] General information about the symbol. ℹ️
        - /stat $[symbol] Key statistics about the symbol. 🔢
        - /help Get some help using the bot. 🆘

**Inline Features**
    You can type @SimpleStockBot `[search]` in any chat or direct message to search for the stock bots
    full list of stock symbols and return the price of the ticker. Then once you select the ticker
    want the bot will send a message as you in that chat with the latest stock price.
    The bot also looks at every message in any chat it is in for stock symbols.Symbols start with a
    `$` followed by the stock symbol. For example:$tsla would return price information for Tesla Motors.
    Market data is provided by [IEX Cloud](https://iexcloud.io)

    If you believe the bot is not behaving properly run `/status`.
    """

    donate_text = """
Simple Stock Bot is run entirely on donations[.](https://www.buymeacoffee.com/Anson)
All donations go directly towards paying for servers, and market data is provided by
[IEX Cloud](https://iexcloud.io/).

The easiest way to donate is to run the `/donate [amount in USD]` command with USdollars you would like to donate.

Example: `/donate 2` would donate 2 USD.
An alternative way to donate is through https://www.buymeacoffee.com/Anson,which accepts Paypal or Credit card.
If you have any questions get in touch: @MisterBiggs or[anson@ansonbiggs.com](http://mailto:anson@ansonbiggs.com/)

_Donations can only be made in a chat directly with @simplestockbot_
    """

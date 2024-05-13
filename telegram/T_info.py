"""Functions and Info specific to the Telegram Bot
"""

import re

import requests as r


class T_info:
    license = re.sub(
        r"\b\n",
        " ",
        r.get("https://gitlab.com/simple-stock-bots/simple-stock-bot/-/raw/master/LICENSE").text,
    )

    help_text = """
Appreciate this bot? Show support by [buying me a beer](https://www.buymeacoffee.com/Anson) 🍻.

Want stock data or to host your own bot? Help keep this bot free by using my
[affiliate link](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=telegram).

📢 Stay updated on the bot's Telegram: https://t.me/simplestockbotnews.

**Guide**: All about using and setting up the bot is in the [docs](https://simplestockbot.com).

The bot recognizes _"Symbols"_. `$` for stocks and `$$` for cryptos. Example:
- `/chart $$eth` gets a month's Ethereum chart.
- `/dividend $psec` shows Prospect Capital's dividend info.

Mention a symbol, and the bot reveals its price.
E.g., `What's $$btc's price since $tsla accepts it?` gives Bitcoin and Tesla prices.

**Commands**
- `/donate [USD]`: Support the bot. 🎗️
- `/intra $[symbol]`: Today's stock activity. 📈
- `/chart $[symbol]`: Past month's stock chart. 📊
- `/trending`: What's hot in stocks and cryptos. 💬
- `/help`: Bot assistance. 🆘

**Inline Features**
Search with @SimpleStockBot `[query]` anywhere.
Pick a ticker, and the bot shares the current price in chat. Note: Prices can lag by an hour.

Data thanks to [marketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=telegram).

Bot issues? Use `/status` or [contact us](https://simplestockbot.com/contact).

    """

    donate_text = """
Support Simple Stock Bot through [donations](https://www.buymeacoffee.com/Anson).
All funds help maintain servers, with data from
[marketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=telegram).

**How to Donate?**
1. Use `/donate [amount in USD]`. E.g., `/donate 2` donates 2 USD.
2. Or, quickly donate at [buymeacoffee](https://www.buymeacoffee.com/Anson). No account needed, accepts Paypal & Credit card.

For questions, visit our [website](https://simplestockbot.com).
"""


# Not used by the bot but for updating commands with BotFather
commands = """
donate - Donate to the bot 🎗️
help - Get some help using the bot. 🆘
trending - Trending Stocks and Cryptos. 💬
intra - $[symbol] Plot since the last market open. 📈
chart - $[chart] Plot of the past month. 📊
"""

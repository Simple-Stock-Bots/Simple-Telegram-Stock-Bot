"""Functions and Info specific to the discord Bot
"""

import re

import requests as r


class D_info:
    license = re.sub(
        r"\b\n",
        " ",
        r.get("https://gitlab.com/simple-stock-bots/simple-stock-bot/-/raw/master/LICENSE").text,
    )

    help_text = """
Thanks for using this bot. If you like it, [support me with a beer](https://www.buymeacoffee.com/Anson). 🍻

For stock data or hosting your own bot, use my link. This helps keep the bot free:
[marketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=discord).

**Updates**: Join the bot's discord: https://t.me/simplestockbotnews.

**Documentation**: All details about the bot are at [docs](https://simplestockbot.com).

The bot reads _"Symbols"_. Use `$` for stock tickers and `$$` for cryptocurrencies. For example:
- `/chart $$eth` gives Ethereum's monthly chart.
- `/dividend $psec` shows Prospect Capital's dividend.

Type any symbol, and the bot shows its price. Like: `Is $$btc rising since $tsla accepts it?` will give Bitcoin and Tesla prices.

**Commands**
- `/donate [USD amount]`: Support the bot. 🎗️
- `/intra $[symbol]`: See stock's latest movement. 📈
- `/chart $[symbol]`: View a month's stock activity. 📊
- `/trending`: Check trending stocks and cryptos. 💬
- `/help`: Need help? Ask here. 🆘

**Inline Features**
Type @SimpleStockBot `[search]` anywhere to find and get stock/crypto prices. Note: Prices might be delayed up to an hour.

Data from: [marketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=discord).

Issues with the bot? Use `/status` or [contact us](https://simplestockbot.com/contact).
    """

    donate_text = """
Simple Stock Bot runs purely on [donations.](https://www.buymeacoffee.com/Anson)
Every donation supports server costs and
[marketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=discord) provides our data.

**How to Donate?**
1. Use `/donate [amount in USD]` command.
   - E.g., `/donate 2` donates 2 USD.
2. Or, donate at [buymeacoffee](https://www.buymeacoffee.com/Anson).
    - It's quick, doesn't need an account, and accepts Paypal or Credit card.

Questions? Visit our [website](https://simplestockbot.com).
"""

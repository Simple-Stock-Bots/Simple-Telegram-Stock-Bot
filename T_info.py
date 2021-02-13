"""Functions and Info specific to the Telegram Bot
"""

import re
import requests as r
import pandas as pd

from typing import List, Dict


class T_info:
    STOCK_REGEX = "[$]([a-zA-Z]{1,4})"
    CRYPTO_REGEX = "[$$]([a-zA-Z]{1,9})"

    def find_symbols(self, text: str) -> List[str, str]:
        """Finds stock tickers starting with a dollar sign, and cryptocurrencies with two dollar signs
        in a blob of text and returns them in a list.
        Only returns each match once. Example: Whats the price of $tsla?

        Parameters
        ----------
        text : str
            Blob of text.

        Returns
        -------
        List[str]
            List of stock symbols as strings without dollar sign.
        """
        symbols = list(set(re.findall(self.SYMBOL_REGEX, text)))
        crypto = list(set(re.findall(self.SYMBOL_REGEX, text)))
        return

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

    def status(self) -> str:
        """Checks IEX Status dashboard for any current API issues.

        Returns
        -------
        str
            Human readable text on status of IEX API
        """

    def price_reply(self, symbols: list) -> Dict[str, str]:
        """Returns current market price or after hours if its available for a given stock symbol.

        Parameters
        ----------
        symbols : list
            List of stock symbols.

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable
            markdown formatted string of the symbols price and movement.
        """

    def dividend_reply(self, symbol: str) -> Dict[str, str]:
        """Returns the most recent, or next dividend date for a stock symbol.

        Parameters
        ----------
        symbols : list
            List of stock symbols.

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable formatted string of the symbols div dates.
        """

    def news_reply(self, symbols: list) -> Dict[str, str]:
        """Gets recent english news on stock symbols.

        Parameters
        ----------
        symbols : list
            List of stock symbols.

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable markdown formatted string of the symbols news.
        """

    def info_reply(self, symbols: List[str]) -> Dict[str, str]:
        """Gets information on stock symbols.

        Parameters
        ----------
        symbols : List[str]
            List of stock symbols.

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable formatted string of the symbols information.
        """

    def intra_reply(self, symbol: str) -> pd.DataFrame:
        """Returns price data for a symbol since the last market open.

        Parameters
        ----------
        symbol : str
            Stock symbol.

        Returns
        -------
        pd.DataFrame
            Returns a timeseries dataframe with high, low, and volume data if its available. Otherwise returns empty pd.DataFrame.
        """

    def chart_reply(self, symbol: str) -> pd.DataFrame:
        """Returns price data for a symbol of the past month up until the previous trading days close.
        Also caches multiple requests made in the same day.

        Parameters
        ----------
        symbol : str
            Stock symbol.

        Returns
        -------
        pd.DataFrame
            Returns a timeseries dataframe with high, low, and volume data if its available. Otherwise returns empty pd.DataFrame.
        """

    def stat_reply(self, symbols: List[str]) -> Dict[str, str]:
        """Gets key statistics for each symbol in the list

        Parameters
        ----------
        symbols : List[str]
            List of stock symbols

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable formatted string of the symbols statistics.
        """

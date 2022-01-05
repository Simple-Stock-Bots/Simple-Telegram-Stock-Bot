"""Function that routes symbols to the correct API provider.
"""

import datetime
import logging
import random
import re
from logging import critical, debug, error, info, warning

import pandas as pd
import schedule
from cachetools import TTLCache, cached

from cg_Crypto import cg_Crypto
from IEX_Symbol import IEX_Symbol
from Symbol import Coin, Stock, Symbol


class Router:
    STOCK_REGEX = "(?:^|[^\\$])\\$([a-zA-Z.]{1,6})"
    CRYPTO_REGEX = "[$]{2}([a-zA-Z]{1,20})"
    trending_count = {}

    def __init__(self):
        self.stock = IEX_Symbol()
        self.crypto = cg_Crypto()

        schedule.every().hour.do(self.trending_decay)

    def trending_decay(self, decay=0.5):
        """Decays the value of each trending stock by a multiplier"""
        t_copy = {}
        dead_keys = []
        if self.trending_count:
            t_copy = self.trending_count.copy()
            for key in t_copy.keys():
                if t_copy[key] < 0.01:
                    # This just makes sure were not keeping around keys that havent been called in a very long time.
                    dead_keys.append(key)
                else:
                    t_copy[key] = t_copy[key] * decay
        for dead in dead_keys:
            t_copy.pop(dead)

        self.trending_count = t_copy.copy()
        info("Decayed trending symbols.")

    def find_symbols(self, text: str, *, trending_weight: int = 1) -> list[Symbol]:
        """Finds stock tickers starting with a dollar sign, and cryptocurrencies with two dollar signs
        in a blob of text and returns them in a list.

        Parameters
        ----------
        text : str
            Blob of text.

        Returns
        -------
        list[Symbol]
            List of stock symbols as Symbol objects
        """
        schedule.run_pending()

        symbols = []
        stocks = set(re.findall(self.STOCK_REGEX, text))
        for stock in stocks:
            sym = self.stock.symbol_list[
                self.stock.symbol_list["symbol"].str.fullmatch(stock, case=False)
            ]
            if ~sym.empty:
                print(sym)
                symbols.append(Stock(sym))
            else:
                info(f"{stock} is not in list of stocks")

        coins = set(re.findall(self.CRYPTO_REGEX, text))
        for coin in coins:
            sym = self.crypto.symbol_list[
                self.crypto.symbol_list["symbol"].str.fullmatch(
                    coin.lower(), case=False
                )
            ]
            if ~sym.empty:
                symbols.append(Coin(sym))
            else:
                info(f"{coin} is not in list of coins")
        if symbols:
            info(symbols)
            for symbol in symbols:
                self.trending_count[symbol.tag] = (
                    self.trending_count.get(symbol.tag, 0) + trending_weight
                )

            return symbols

    def status(self, bot_resp) -> str:
        """Checks for any issues with APIs.

        Returns
        -------
        str
            Human readable text on status of the bot and relevant APIs
        """

        stats = f"""
        Bot Status:
        {bot_resp}

        Stock Market Data:
        {self.stock.status()}

        Cryptocurrency Data:
        {self.crypto.status()}
        """

        warning(stats)

        return stats

    def inline_search(self, search: str, matches: int = 5) -> pd.DataFrame:
        """Searches based on the shortest symbol that contains the same string as the search.
        Should be very fast compared to a fuzzy search.

        Parameters
        ----------
        search : str
            String used to match against symbols.

        Returns
        -------
        list[tuple[str, str]]
            Each tuple contains: (Symbol, Issue Name).
        """

        df = pd.concat([self.stock.symbol_list, self.crypto.symbol_list])

        df = df[
            df["description"].str.contains(search, regex=False, case=False)
        ].sort_values(by="type_id", key=lambda x: x.str.len())

        symbols = df.head(matches)
        symbols["price_reply"] = symbols["type_id"].apply(
            lambda sym: self.price_reply(self.find_symbols(sym, trending_weight=0))[0]
        )

        return symbols

    def price_reply(self, symbols: list[Symbol]) -> list[str]:
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
        replies = []

        for symbol in symbols:
            info(symbol)
            if isinstance(symbol, Stock):
                replies.append(self.stock.price_reply(symbol))
            elif isinstance(symbol, Coin):
                replies.append(self.crypto.price_reply(symbol))
            else:
                info(f"{symbol} is not a Stock or Coin")

        return replies

    def dividend_reply(self, symbols: list) -> list[str]:
        """Returns the most recent, or next dividend date for a stock symbol.

        Parameters
        ----------
        symbols : list
            List of stock symbols.

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable
                formatted string of the symbols div dates.
        """
        replies = []
        for symbol in symbols:
            if isinstance(symbol, Stock):
                replies.append(self.stock.dividend_reply(symbol))
            elif isinstance(symbol, Coin):
                replies.append("Cryptocurrencies do no have Dividends.")
            else:
                debug(f"{symbol} is not a Stock or Coin")

        return replies

    def news_reply(self, symbols: list) -> list[str]:
        """Gets recent english news on stock symbols.

        Parameters
        ----------
        symbols : list
            List of stock symbols.

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human
                readable markdown formatted string of the symbols news.
        """
        replies = []

        for symbol in symbols:
            if isinstance(symbol, Stock):
                replies.append(self.stock.news_reply(symbol))
            elif isinstance(symbol, Coin):
                # replies.append(self.crypto.news_reply(symbol))
                replies.append(
                    "News is not yet supported for cryptocurrencies. If you have any suggestions for news sources please contatct @MisterBiggs"
                )
            else:
                debug(f"{symbol} is not a Stock or Coin")

        return replies

    def info_reply(self, symbols: list) -> list[str]:
        """Gets information on stock symbols.

        Parameters
        ----------
        symbols : list[str]
            List of stock symbols.

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable formatted
                string of the symbols information.
        """
        replies = []

        for symbol in symbols:
            if isinstance(symbol, Stock):
                replies.append(self.stock.info_reply(symbol))
            elif isinstance(symbol, Coin):
                replies.append(self.crypto.info_reply(symbol))
            else:
                debug(f"{symbol} is not a Stock or Coin")

        return replies

    def intra_reply(self, symbol: Symbol) -> pd.DataFrame:
        """Returns price data for a symbol since the last market open.

        Parameters
        ----------
        symbol : str
            Stock symbol.

        Returns
        -------
        pd.DataFrame
            Returns a timeseries dataframe with high, low, and volume data if its available.
                Otherwise returns empty pd.DataFrame.
        """

        if isinstance(symbol, Stock):
            return self.stock.intra_reply(symbol)
        elif isinstance(symbol, Coin):
            return self.crypto.intra_reply(symbol)
        else:
            debug(f"{symbol} is not a Stock or Coin")
            return pd.DataFrame()

    def chart_reply(self, symbol: Symbol) -> pd.DataFrame:
        """Returns price data for a symbol of the past month up until the previous trading days close.
        Also caches multiple requests made in the same day.

        Parameters
        ----------
        symbol : str
            Stock symbol.

        Returns
        -------
        pd.DataFrame
            Returns a timeseries dataframe with high, low, and volume data if its available.
                Otherwise returns empty pd.DataFrame.
        """
        if isinstance(symbol, Stock):
            return self.stock.chart_reply(symbol)
        elif isinstance(symbol, Coin):
            return self.crypto.chart_reply(symbol)
        else:
            debug(f"{symbol} is not a Stock or Coin")
            return pd.DataFrame()

    def stat_reply(self, symbols: list[Symbol]) -> list[str]:
        """Gets key statistics for each symbol in the list

        Parameters
        ----------
        symbols : list[str]
            List of stock symbols

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable
                formatted string of the symbols statistics.
        """
        replies = []

        for symbol in symbols:
            if isinstance(symbol, Stock):
                replies.append(self.stock.stat_reply(symbol))
            elif isinstance(symbol, Coin):
                replies.append(self.crypto.stat_reply(symbol))
            else:
                debug(f"{symbol} is not a Stock or Coin")

        return replies

    def cap_reply(self, symbols: list[Symbol]) -> list[str]:
        """Gets market cap for each symbol in the list

        Parameters
        ----------
        symbols : list[str]
            List of stock symbols

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable
                formatted string of the symbols market cap.
        """
        replies = []

        for symbol in symbols:
            if isinstance(symbol, Stock):
                replies.append(self.stock.cap_reply(symbol))
            elif isinstance(symbol, Coin):
                replies.append(self.crypto.cap_reply(symbol))
            else:
                debug(f"{symbol} is not a Stock or Coin")

        return replies

    def spark_reply(self, symbols: list[Symbol]) -> list[str]:
        """Gets change for each symbol and returns it in a compact format

        Parameters
        ----------
        symbols : list[str]
            List of stock symbols

        Returns
        -------
        list[str]
            List of human readable strings.
        """
        replies = []

        for symbol in symbols:
            if isinstance(symbol, Stock):
                replies.append(self.stock.spark_reply(symbol))
            elif isinstance(symbol, Coin):
                replies.append(self.crypto.spark_reply(symbol))
            else:
                debug(f"{symbol} is not a Stock or Coin")

        return replies

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def trending(self) -> str:
        """Checks APIs for trending symbols.

        Returns
        -------
        list[str]
            List of preformatted strings to be sent to user.
        """

        stocks = self.stock.trending()
        coins = self.crypto.trending()

        reply = ""

        if self.trending_count:
            reply += "🔥Trending on the Stock Bot:\n`"
            reply += "━" * len("Trending on the Stock Bot:") + "`\n"

            sorted_trending = [
                s[0]
                for s in sorted(self.trending_count.items(), key=lambda item: item[1])
            ][::-1][0:5]

            for t in sorted_trending:
                reply += self.spark_reply(self.find_symbols(t))[0] + "\n"

        if stocks:
            reply += "\n\n💵Trending Stocks:\n`"
            reply += "━" * len("Trending Stocks:") + "`\n"
            for stock in stocks:
                reply += stock + "\n"

        if coins:
            reply += "\n\n🦎Trending Crypto:\n`"
            reply += "━" * len("Trending Crypto:") + "`\n"
            for coin in coins:
                reply += coin + "\n"

        if "`$GME" in reply:
            reply = reply.replace("🔥", "🦍")

        if reply:
            return reply
        else:
            warning("Failed to collect trending data.")
            return "Trending data is not currently available."

    def random_pick(self) -> str:

        choice = random.choice(
            list(self.stock.symbol_list["description"])
            + list(self.crypto.symbol_list["description"])
        )
        hold = (
            datetime.date.today() + datetime.timedelta(random.randint(1, 365))
        ).strftime("%b %d, %Y")

        return f"{choice}\nBuy and hold until: {hold}"

    def batch_price_reply(self, symbols: list[Symbol]) -> list[str]:
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
        replies = []
        stocks = []
        coins = []

        for symbol in symbols:
            if isinstance(symbol, Stock):
                stocks.append(symbol)
            elif isinstance(symbol, Coin):
                coins.append(symbol)
            else:
                debug(f"{symbol} is not a Stock or Coin")

        if stocks:
            # IEX batch endpoint doesnt seem to be working right now
            for stock in stocks:
                replies.append(self.stock.price_reply(stock))
        if coins:
            replies = replies + self.crypto.batch_price(coins)

        return replies

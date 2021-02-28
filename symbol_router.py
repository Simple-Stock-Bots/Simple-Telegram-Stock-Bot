"""Function that routes symbols to the correct API provider.
"""

import re
import requests as r
import pandas as pd

from typing import List, Dict

from IEX_Symbol import IEX_Symbol
from cg_Crypto import cg_Crypto


class Router:
    STOCK_REGEX = "(?:^|[^\\$])\\$([a-zA-Z]{1,4})"
    CRYPTO_REGEX = "[$]{2}([a-zA-Z]{1,9})"

    def __init__(self):
        self.stock = IEX_Symbol()
        self.crypto = cg_Crypto()

    def find_symbols(self, text: str) -> Dict[str, str]:
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
        symbols = []
        stocks = set(re.findall(self.STOCK_REGEX, text))
        for stock in stocks:
            if stock.upper() in self.stock.symbol_list["symbol"].values:
                symbols.append(Stock(stock))
            else:
                print(f"{stock} is not in list of stocks")

        coins = set(re.findall(self.CRYPTO_REGEX, text))
        for coin in coins:
            if coin.lower() in self.crypto.symbol_list["symbol"].values:
                symbols.append(Coin(coin.lower()))
            else:
                print(f"{coin} is not in list of coins")

        return symbols

    def status(self) -> str:
        """Checks for any issues with APIs.

        Returns
        -------
        str
            Human readable text on status of IEX API
        """

    def search_symbols(self, search: str) -> List[str]:
        """Performs a fuzzy search to find stock symbols closest to a search term.

        Parameters
        ----------
        search : str
            String used to search, could be a company name or something close to the companies stock ticker.

        Returns
        -------
        List[tuple[str, str]]
            A list tuples of every stock sorted in order of how well they match. Each tuple contains: (Symbol, Issue Name).
        """
        # TODO add support for crypto
        return self.stock.find_symbols(search)

    def price_reply(self, symbols: dict) -> List[str]:
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
            if isinstance(symbol, Stock):
                replies.append(self.stock.price_reply(symbol))
            elif isinstance(symbol, Coin):
                replies.append(self.crypto.price_reply(symbol))
            else:
                print(f"{symbol} is not a Stock or Coin")
        print(replies)
        return replies

    def dividend_reply(self, symbols: dict) -> Dict[str, str]:
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
        replies = []

        if symbols["stocks"]:
            for s in symbols["stocks"]:
                replies.append(self.stock.price_reply(s))

        if symbols["crypto"]:
            replies.append("Cryptocurrencies do no have Dividends.")

    def news_reply(self, symbols: dict) -> List[str]:
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
        replies = []

        if symbols["stocks"]:
            for s in symbols["stocks"]:
                replies.append(self.stock.price_reply(s))

        if symbols["crypto"]:
            for s in symbols["crypto"]:
                replies.append(self.crypto.price_reply(s))

        return replies

    def info_reply(self, symbols: dict) -> List[str]:
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
        replies = []

        if symbols["stocks"]:
            for s in symbols["stocks"]:
                replies.append(self.stock.price_reply(s))

        if symbols["crypto"]:
            for s in symbols["crypto"]:
                replies.append(self.crypto.price_reply(s))

        return replies

    def intra_reply(self, symbol: str, type: str) -> pd.DataFrame:
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
        if type == "stocks":
            return self.stock.intra_reply(symbol)
        elif type == "crypto":
            return self.crypto.intra_reply(symbol)
        else:
            raise f"Unknown type: {type}"

    def chart_reply(self, symbols: str) -> pd.DataFrame:
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
        if symbols["stocks"]:
            return self.stock.intra_reply(symbol := symbols["stocks"][0]), symbol
        if symbols["crypto"]:
            return self.stock.intra_reply(symbol := symbols["crypto"][0]), symbol

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
        replies = []

        if symbols["stocks"]:
            for s in symbols["stocks"]:
                replies.append(self.stock.price_reply(s))

        if symbols["crypto"]:
            for s in symbols["crypto"]:
                replies.append(self.crypto.price_reply(s))


class Symbol:
    currency = "usd"
    pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} instance of {self.id} at {id(self)}"


class Stock(Symbol):
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.id = symbol


class Coin(Symbol):
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.get_data()

    def get_data(self) -> None:
        self.id = cg_Crypto().symbol_id(self.symbol)
        data = r.get("https://api.coingecko.com/api/v3/coins/" + self.id).json()
        self.data = data

        self.name = data["name"]
        self.description = data["description"]
        self.price = data["market_data"]["current_price"][self.currency]
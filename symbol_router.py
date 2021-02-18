"""Function that routes symbols to the correct API provider. 
"""

import re
import requests as r
import pandas as pd

from typing import List, Dict

from IEX_Symbol import IEX_Symbol
from cg_Crypto import cg_Crypto


class Router:
    STOCK_REGEX = "[$]([a-zA-Z]{1,4})"
    CRYPTO_REGEX = "[$$]([a-zA-Z]{1,9})"

    def __init__(self, IEX_TOKEN=""):
        self.symbol = IEX_Symbol(IEX_TOKEN)
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
        symbols = {}
        symbols["stocks"] = list(set(re.findall(self.SYMBOL_REGEX, text)))
        symbols["crypto"] = list(set(re.findall(self.SYMBOL_REGEX, text)))
        return symbols

    def status(self) -> str:
        """Checks for any issues with APIs.

        Returns
        -------
        str
            Human readable text on status of IEX API
        """

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

        if symbols["stocks"]:
            for s in symbols["stocks"]:
                replies.append(self.symbol.price_reply(s))

        if symbols["crypto"]:
            for s in symbols["crypto"]:
                replies.append(self.crypto.price_reply(s))

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
                replies.append(self.symbol.price_reply(s))

        if symbols["crypto"]:
            for s in symbols["crypto"]:
                replies.append(self.crypto.price_reply(s))

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
                replies.append(self.symbol.price_reply(s))

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
                replies.append(self.symbol.price_reply(s))

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
            return self.symbol.intra_reply(symbol)
        elif type == "crypto":
            return self.crypto.intra_reply(symbol)
        else:
            raise f"Unknown type: {type}"

    def chart_reply(self, symbol: str, type: str) -> pd.DataFrame:
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
        if type == "stocks":
            return self.symbol.intra_reply(symbol)
        elif type == "crypto":
            return self.crypto.intra_reply(symbol)
        else:
            raise f"Unknown type: {type}"

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
                replies.append(self.symbol.price_reply(s))

        if symbols["crypto"]:
            for s in symbols["crypto"]:
                replies.append(self.crypto.price_reply(s))
import pandas as pd
import logging


class Symbol:
    """
    symbol: What the user calls it. ie tsla or btc
    id: What the api expects. ie tsla or bitcoin
    name: Human readable. ie Tesla or Bitcoin
    tag: Uppercase tag to call the symbol. ie $TSLA or $$BTC
    """

    currency = "usd"
    pass

    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.id = symbol
        self.name = symbol
        self.tag = "$" + symbol

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} instance of {self.id} at {id(self)}>"

    def __str__(self) -> str:
        return self.id


class Stock(Symbol):
    """Stock Market Object. Gets data from IEX Cloud"""

    def __init__(self, symbol: pd.DataFrame) -> None:
        if len(symbol) > 1:
            logging.info(f"Crypto with shared id:\n\t{symbol.id}")
            symbol = symbol.head(1)

        self.symbol = symbol.symbol.values[0]
        self.id = symbol.id.values[0]
        self.name = symbol.name.values[0]
        self.tag = symbol.type_id.values[0].upper()


class Coin(Symbol):
    """Cryptocurrency Object. Gets data from CoinGecko."""

    def __init__(self, symbol: pd.DataFrame) -> None:
        if len(symbol) > 1:
            logging.info(f"Crypto with shared id:\n\t{symbol.id}")
            symbol = symbol.head(1)

        self.symbol = symbol.symbol.values[0]
        self.id = symbol.id.values[0]
        self.name = symbol.name.values[0]
        self.tag = symbol.type_id.values[0].upper()

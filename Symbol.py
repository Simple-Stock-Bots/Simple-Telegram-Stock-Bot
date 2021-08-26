import functools

import requests as r


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

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.id = symbol
        self.name = "$" + symbol.upper()
        self.tag = "$" + symbol.upper()


# Used by Coin to change symbols for ids
coins = r.get("https://api.coingecko.com/api/v3/coins/list").json()


class Coin(Symbol):
    """Cryptocurrency Object. Gets data from CoinGecko."""

    @functools.cache
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.tag = "$$" + symbol.upper()
        self.get_data()

    def get_data(self) -> None:
        self.id = list(filter(lambda coin: coin["symbol"] == self.symbol, coins))[0][
            "id"
        ]
        data = r.get("https://api.coingecko.com/api/v3/coins/" + self.id).json()
        self.data = data

        self.name = data["name"]
        self.description = data["description"]
        # self.price = data["market_data"]["current_price"][self.currency]

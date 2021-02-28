import requests as r
from cg_Crypto import cg_Crypto


class Symbol:
    """
    symbol: What the user calls it. ie tsla or btc
    id: What the api expects. ie tsla or bitcoin
    name: Human readable. ie Tesla or Bitcoin
    """

    currency = "usd"
    pass

    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.id = symbol
        self.name = symbol

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} instance of {self.id} at {id(self)}>"

    def __str__(self) -> str:
        return self.id


class Stock(Symbol):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.id = symbol


# This is so every Coin instance doesnt have to download entire list of coin symbols and id's
cg = cg_Crypto()


class Coin(Symbol):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.get_data()

    def get_data(self) -> None:
        self.id = cg.symbol_id(self.symbol)
        data = r.get("https://api.coingecko.com/api/v3/coins/" + self.id).json()
        self.data = data

        self.name = data["name"]
        self.description = data["description"]
        self.price = data["market_data"]["current_price"][self.currency]

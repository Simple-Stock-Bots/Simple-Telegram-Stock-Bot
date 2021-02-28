import requests as r


class Symbol:
    currency = "usd"
    pass


class Stock(Symbol):
    def __init__(self, symbol) -> None:
        self.symbol = symbol


class Coin(Symbol):
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.get_data()

    def get_data(self) -> None:
        data = r.get("https://api.coingecko.com/api/v3/coins/" + self.symbol).json()

        self.id = data["id"]
        self.name = data["name"]
        self.description = data["description"]
        self.price = data["market_data"]["current_price"][self.currency]

        self.data = data

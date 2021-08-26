"""Class with functions for running the bot with IEX Cloud.
"""

# import logging
# import os
# from datetime import datetime
# from logging import warning
# from typing import List, Optional, Tuple

# import pandas as pd
# import requests as r
# import schedule
# from fuzzywuzzy import fuzz

from Symbol import Stock


class IEX_Symbol:
    def price_reply(self, symbol: Stock) -> str:
        return "Stock market data is currently unavailable see: https://t.me/simplestockbotnews\nCryptocurrency data is still available."

    def dividend_reply(self, symbol: Stock) -> str:
        return "Stock market data is currently unavailable see: https://t.me/simplestockbotnews\nCryptocurrency data is still available."

    def news_reply(self, symbol: Stock) -> str:
        return "Stock market data is currently unavailable see: https://t.me/simplestockbotnews\nCryptocurrency data is still available."

    def info_reply(self, symbol: Stock) -> str:
        return "Stock market data is currently unavailable see: https://t.me/simplestockbotnews\nCryptocurrency data is still available."

    def stat_reply(self, symbol: Stock) -> str:
        return "Stock market data is currently unavailable see: https://t.me/simplestockbotnews\nCryptocurrency data is still available."

    def cap_reply(self, symbol: Stock) -> str:
        return "Stock market data is currently unavailable see: https://t.me/simplestockbotnews\nCryptocurrency data is still available."

    def trending(self) -> list[str]:
        return [
            "Stock market data is currently unavailable see: https://t.me/simplestockbotnews\nCryptocurrency data is still available."
        ]

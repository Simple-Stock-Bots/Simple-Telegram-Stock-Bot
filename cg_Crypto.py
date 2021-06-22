"""Class with functions for running the bot with IEX Cloud.
"""

from datetime import datetime
from typing import Optional, List, Tuple

import pandas as pd
import requests as r
import schedule
from fuzzywuzzy import fuzz
from markdownify import markdownify
from Symbol import Coin


class cg_Crypto:
    """
    Functions for finding crypto info
    """

    vs_currency = "usd"  # simple/supported_vs_currencies for list of options

    searched_symbols = {}

    def __init__(self) -> None:
        """Creates a Symbol Object

        Parameters
        ----------
        IEX_TOKEN : str
            IEX Token
        """
        self.get_symbol_list()
        schedule.every().day.do(self.get_symbol_list)

    def symbol_id(self, symbol) -> str:
        try:
            return self.symbol_list[self.symbol_list["symbol"] == symbol]["id"].values[
                0
            ]
        except KeyError:
            return ""

    def get_symbol_list(
        self, return_df=False
    ) -> Optional[Tuple[pd.DataFrame, datetime]]:

        raw_symbols = r.get(
            "https://api.coingecko.com/api/v3/coins/list",
            timeout=5,
        ).json()
        symbols = pd.DataFrame(data=raw_symbols)

        symbols["description"] = (
            "$$" + symbols["symbol"].str.upper() + ": " + symbols["name"]
        )
        symbols = symbols[["id", "symbol", "name", "description"]]
        symbols["type_id"] = "$$" + symbols["id"]

        self.symbol_list = symbols
        if return_df:
            return symbols, datetime.now()

    def status(self) -> str:
        """Checks CoinGecko /ping endpoint for API issues.

        Returns
        -------
        str
            Human readable text on status of CoinGecko API
        """
        status = r.get(
            "https://api.coingecko.com/api/v3/ping",
            timeout=5,
        )

        if status.status_code == 200:
            return f"CoinGecko API responded that it was OK in {status.elapsed.total_seconds()} Seconds."
        else:
            return f"CoinGecko API returned an error in {status.elapsed.total_seconds()} Seconds."

    def search_symbols(self, search: str) -> List[Tuple[str, str]]:
        """Performs a fuzzy search to find coin symbols closest to a search term.

        Parameters
        ----------
        search : str
            String used to search, could be a company name or something close to the companies coin ticker.

        Returns
        -------
        List[tuple[str, str]]
            A list tuples of every coin sorted in order of how well they match. Each tuple contains: (Symbol, Issue Name).
        """
        schedule.run_pending()
        search = search.lower()
        try:  # https://stackoverflow.com/a/3845776/8774114
            return self.searched_symbols[search]
        except KeyError:
            pass

        symbols = self.symbol_list
        symbols["Match"] = symbols.apply(
            lambda x: fuzz.ratio(search, f"{x['symbol']}".lower()),
            axis=1,
        )

        symbols.sort_values(by="Match", ascending=False, inplace=True)
        if symbols["Match"].head().sum() < 300:
            symbols["Match"] = symbols.apply(
                lambda x: fuzz.partial_ratio(search, x["name"].lower()),
                axis=1,
            )

            symbols.sort_values(by="Match", ascending=False, inplace=True)
        symbols = symbols.head(10)
        symbol_list = list(zip(list(symbols["symbol"]), list(symbols["description"])))
        self.searched_symbols[search] = symbol_list
        return symbol_list

    def price_reply(self, symbol: Coin) -> str:
        """Returns current market price or after hours if its available for a given coin symbol.

        Parameters
        ----------
        symbols : list
            List of coin symbols.

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable
            markdown formatted string of the symbols price and movement.
        """

        response = r.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol.id}?localization=false",
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()

            try:
                name = data["name"]
                price = data["market_data"]["current_price"][self.vs_currency]
                change = data["market_data"]["price_change_percentage_24h"]
                if change is None:
                    change = 0
            except KeyError:
                return f"{symbol} returned an error."

            message = f"The current price of {name} is $**{price:,}**"

            # Determine wording of change text
            if change > 0:
                message += f", the coin is currently **up {change:.3f}%** for today"
            elif change < 0:
                message += f", the coin is currently **down {change:.3f}%** for today"
            else:
                message += ", the coin hasn't shown any movement today."

        else:
            message = f"The Coin: {symbol.name} was not found."

        return message

    def intra_reply(self, symbol: Coin) -> pd.DataFrame:
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
        response = r.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol.id}/ohlc?vs_currency=usd&days=1",
            timeout=5,
        )
        if response.status_code == 200:
            df = pd.DataFrame(
                response.json(), columns=["Date", "Open", "High", "Low", "Close"]
            ).dropna()
            df["Date"] = pd.to_datetime(df["Date"], unit="ms")
            df = df.set_index("Date")
            return df

        return pd.DataFrame()

    def chart_reply(self, symbol: Coin) -> pd.DataFrame:
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
        response = r.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol.id}/ohlc?vs_currency=usd&days=30",
            timeout=5,
        )

        if response.status_code == 200:
            df = pd.DataFrame(
                response.json(), columns=["Date", "Open", "High", "Low", "Close"]
            ).dropna()
            df["Date"] = pd.to_datetime(df["Date"], unit="ms")
            df = df.set_index("Date")
            return df

        return pd.DataFrame()

    def stat_reply(self, symbol: Coin) -> str:
        """Gets key statistics for each symbol in the list

        Parameters
        ----------
        symbols : List[str]
            List of coin symbols

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable formatted string of the symbols statistics.
        """
        response = r.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol.id}?localization=false",
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()

            return f"""
                [{data['name']}]({data['links']['homepage'][0]}) Statistics:
                Market Cap: ${data['market_data']['market_cap'][self.vs_currency]:,}
                Market Cap Ranking: {data.get('market_cap_rank',"Not Available")}
                CoinGecko Scores:
                    Overall: {data.get('coingecko_score','Not Available')}
                    Development: {data.get('developer_score','Not Available')}
                    Community: {data.get('community_score','Not Available')}
                    Public Interest: {data.get('public_interest_score','Not Available')}
                    """
        else:
            return f"{symbol.symbol} returned an error."

    def info_reply(self, symbol: Coin) -> str:
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

        response = r.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol.id}?localization=false",
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            try:
                return markdownify(data["description"]["en"])
            except KeyError:
                return f"{symbol} does not have a description available."

        return f"No information found for: {symbol}\nEither today is boring or the symbol does not exist."

    def trending(self) -> list[str]:
        """Gets current coins trending on coingecko

        Returns
        -------
        list[str]
            list of $$ID: NAME
        """

        coins = r.get(
            "https://api.coingecko.com/api/v3/search/trending",
            timeout=5,
        )
        try:
            trending = []
            if coins.status_code == 200:
                for coin in coins.json()["coins"]:
                    c = coin["item"]

                    sym = c["symbol"].upper()
                    name = c["name"]
                    change = r.get(
                        f"https://api.coingecko.com/api/v3/simple/price?ids={c['id']}&vs_currencies={self.vs_currency}&include_24hr_change=true"
                    ).json()[c["id"]]["usd_24h_change"]

                    msg = f"`$${sym}`: {name}, {change:.2f}%"

                    trending.append(msg)

        except Exception as e:
            print(e)
            trending = ["Trending Coins Currently Unavailable."]

        return trending

    def batch_price(self, coins: list[Coin]) -> list[str]:
        query = ",".join([c.id for c in coins])

        prices = r.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={query}&vs_currencies=usd&include_24hr_change=true",
            timeout=5,
        ).json()

        replies = []
        for coin in coins:
            if coin.id in prices:
                p = prices[coin.id]

                if p.get("usd_24h_change") is None:
                    p["usd_24h_change"] = 0

                replies.append(
                    f"{coin.name}: ${p.get('usd',0):,} and has moved {p.get('usd_24h_change',0.0):.2f}% in the past 24 hours."
                )

        return replies

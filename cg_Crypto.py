"""Class with functions for running the bot with IEX Cloud.
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

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
    trending_cache = None

    def __init__(self) -> None:
        """Creates a Symbol Object

        Parameters
        ----------
        IEX_TOKEN : str
            IEX Token
        """
        self.get_symbol_list()
        schedule.every().day.do(self.get_symbol_list)

    def get(self, endpoint, params: dict = {}, timeout=10) -> dict:

        url = "https://api.coingecko.com/api/v3" + endpoint
        resp = r.get(url, params=params, timeout=timeout)
        # Make sure API returned a proper status code
        try:
            resp.raise_for_status()
        except r.exceptions.HTTPError as e:
            logging.error(e)
            return {}

        # Make sure API returned valid JSON
        try:
            resp_json = resp.json()
            return resp_json
        except r.exceptions.JSONDecodeError as e:
            logging.error(e)
            return {}

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

        raw_symbols = self.get("/coins/list")
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

        try:
            status.raise_for_status()
            return f"CoinGecko API responded that it was OK with a {status.status_code} in {status.elapsed.total_seconds()} Seconds."
        except:
            return f"CoinGecko API returned an error code {status.status_code} in {status.elapsed.total_seconds()} Seconds."

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

    def price_reply(self, coin: Coin) -> str:
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

        if resp := self.get(
            "/simple/price",
            params={
                "ids": coin.id,
                "vs_currencies": self.vs_currency,
                "include_24hr_change": "true",
            },
        ):
            try:
                data = resp[coin.id]

                price = data[self.vs_currency]
                change = data[self.vs_currency + "_24h_change"]
                if change is None:
                    change = 0
            except KeyError:
                return f"{coin.id} returned an error."

            message = f"The current price of {coin.name} is $**{price:,}**"

            # Determine wording of change text
            if change > 0:
                message += f", the coin is currently **up {change:.3f}%** for today"
            elif change < 0:
                message += f", the coin is currently **down {change:.3f}%** for today"
            else:
                message += ", the coin hasn't shown any movement today."

        else:
            message = f"The price for {coin.name} is not available. If you suspect this is an error run `/status`"

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

        if resp := self.get(
            f"/coins/{symbol.id}/ohlc",
            params={"vs_currency": self.vs_currency, "days": 1},
        ):
            df = pd.DataFrame(
                resp, columns=["Date", "Open", "High", "Low", "Close"]
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

        if resp := self.get(
            f"/coins/{symbol.id}/ohlc",
            params={"vs_currency": self.vs_currency, "days": 30},
        ):
            df = pd.DataFrame(
                resp, columns=["Date", "Open", "High", "Low", "Close"]
            ).dropna()
            df["Date"] = pd.to_datetime(df["Date"], unit="ms")
            df = df.set_index("Date")
            return df

        return pd.DataFrame()

    def stat_reply(self, symbol: Coin) -> str:
        """Gathers key statistics on coin. Mostly just CoinGecko scores.

        Parameters
        ----------
        symbol : Coin

        Returns
        -------
        str
            Preformatted markdown.
        """

        if data := self.get(
            f"/coins/{symbol.id}",
            params={
                "localization": "false",
            },
        ):

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

    def cap_reply(self, coin: Coin) -> str:
        """Gets market cap for Coin

        Parameters
        ----------
        coin : Coin

        Returns
        -------
        str
            Preformatted markdown.
        """

        if resp := self.get(
            f"/simple/price",
            params={
                "ids": coin.id,
                "vs_currencies": self.vs_currency,
                "include_market_cap": "true",
            },
        ):
            print(resp)
            try:
                data = resp[coin.id]

                price = data[self.vs_currency]
                cap = data[self.vs_currency + "_market_cap"]
            except KeyError:
                return f"{coin.id} returned an error."

            if cap == 0:
                return f"The market cap for {coin.name} is not available for unknown reasons."

            message = f"The current price of {coin.name} is $**{price:,}** and its market cap is $**{cap:,.2f}** {self.vs_currency.upper()}"

        else:
            message = f"The Coin: {coin.name} was not found or returned and error."

        return message

    def info_reply(self, symbol: Coin) -> str:
        """Gets coin description

        Parameters
        ----------
        symbol : Coin

        Returns
        -------
        str
            Preformatted markdown.
        """

        if data := self.get(
            f"/coins/{symbol.id}",
            params={"localization": "false"},
        ):
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
            list of $$ID: NAME, CHANGE%
        """

        coins = self.get("/search/trending")
        try:
            trending = []
            for coin in coins["coins"]:
                c = coin["item"]

                sym = c["symbol"].upper()
                name = c["name"]
                change = self.get(
                    f"/simple/price",
                    params={
                        "ids": c["id"],
                        "vs_currencies": self.vs_currency,
                        "include_24hr_change": "true",
                    },
                )[c["id"]]["usd_24h_change"]

                msg = f"`$${sym}`: {name}, {change:.2f}%"

                trending.append(msg)

        except Exception as e:
            logging.warning(e)
            return self.trending_cache

        self.trending_cache = trending
        return trending

    def batch_price(self, coins: list[Coin]) -> list[str]:
        """Gets price of a list of coins all in one API call

        Parameters
        ----------
        coins : list[Coin]

        Returns
        -------
        list[str]
            returns preformatted list of strings detailing price movement of each coin passed in.
        """
        query = ",".join([c.id for c in coins])

        prices = self.get(
            f"/simple/price",
            params={
                "ids": query,
                "vs_currencies": self.vs_currency,
                "include_24hr_change": "true",
            },
        )

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

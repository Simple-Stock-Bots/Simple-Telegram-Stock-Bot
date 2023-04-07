"""Class with functions for running the bot with IEX Cloud.
"""

import logging
import os
import datetime as dt
from logging import warning
from typing import Dict

import pandas as pd
import requests as r
import schedule

from Symbol import Stock


class MarketData:
    """
    Functions for finding stock market information about symbols from MarkData.app
    """

    SYMBOL_REGEX = "[$]([a-zA-Z]{1,4})"

    charts: Dict[Stock, pd.DataFrame] = {}

    def __init__(self) -> None:
        """Creates a Symbol Object

        Parameters
        ----------
        MARKETDATA_TOKEN : str
            MarketData.app API Token
        """
        try:
            self.MARKETDATA_TOKEN = os.environ["MARKETDATA"]

            if self.MARKETDATA_TOKEN == "TOKEN":
                self.MARKETDATA_TOKEN = ""
        except KeyError:
            self.MARKETDATA_TOKEN = ""
            warning("Starting without an MarketData.app Token will not allow you to get market data!")

        if self.MARKETDATA_TOKEN != "":
            schedule.every().day.do(self.clear_charts)

    def get(self, endpoint, params: dict = {}, timeout=10) -> dict:
        url = "https://api.marketdata.app/v1/" + endpoint

        # set token param if it wasn't passed.
        params["token"] = params.get("token", self.MARKETDATA_TOKEN)

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

            match resp_json["s"]:
                case "ok":
                    return resp_json
                case "no_data":
                    return resp_json
                case "error":
                    logging.error("MarketData Error:\n" + resp_json["errmsg"])
                    return {}

        except r.exceptions.JSONDecodeError as e:
            logging.error(e)

        return {}

    def clear_charts(self) -> None:
        """
        Clears cache of chart data.
        Charts are cached so that only 1 API call per 24 hours is needed since the
            chart data is expensive and a large download.
        """
        self.charts = {}

    def status(self) -> str:
        return "status isnt implemented by marketdata.app"

    def price_reply(self, symbol: Stock) -> str:
        """Returns price movement of Stock for the last market day, or after hours.

        Parameters
        ----------
        symbol : Stock

        Returns
        -------
        str
            Formatted markdown
        """

        if quoteResp := self.get(f"stocks/quotes/{symbol}/"):
            return f"The current price of {quoteResp['symbol']} is ${quoteResp['last']}"

        else:
            return f"Getting a quote for {symbol} encountered an error."

    def intra_reply(self, symbol: Stock) -> pd.DataFrame:
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
        schedule.run_pending()

        try:
            return self.charts[symbol.id.upper()]
        except KeyError:
            pass

        resolution = "5"  # minutes

        if data := self.get(
            f"stocks/candles/{resolution}/{symbol}",
            params={
                "from": dt.datetime.now().strftime("%Y-%m-%d"),
                "to": dt.datetime.now().isoformat(),
            },
        ):
            data.pop("s")
            df = pd.DataFrame(data)
            df["t"] = pd.to_datetime(df["t"], unit="s")
            df.set_index("t", inplace=True)

            df.rename(
                columns={
                    "o": "Open",
                    "h": "High",
                    "l": "Low",
                    "c": "Close",
                    "v": "Volume",
                },
                inplace=True,
            )

            self.charts[symbol.id.upper()] = df
            return df

        return pd.DataFrame()

    def chart_reply(self, symbol: Stock) -> pd.DataFrame:
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
        schedule.run_pending()

        try:
            return self.charts[symbol.id.upper()]
        except KeyError:
            pass

        to_date = dt.datetime.today().strftime("%Y-%m-%d")
        from_date = (dt.datetime.today() - dt.timedelta(days=30)).strftime("%Y-%m-%d")
        resultion = "daily"

        if data := self.get(
            f"stocks/candles/{resultion}/{symbol}",
            params={
                "from": from_date,
                "to": to_date,
            },
        ):
            data.pop("s")

            df = pd.DataFrame(data)
            df["t"] = pd.to_datetime(df["t"], unit="s")
            df.set_index("t", inplace=True)

            df.rename(
                columns={
                    "o": "Open",
                    "h": "High",
                    "l": "Low",
                    "c": "Close",
                    "v": "Volume",
                },
                inplace=True,
            )

            self.charts[symbol.id.upper()] = df
            return df

        return pd.DataFrame()

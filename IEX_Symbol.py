"""Class with functions for running the bot with IEX Cloud.
"""

import logging
import os
from datetime import datetime
from logging import warning
from typing import List, Optional, Tuple

import pandas as pd
import requests as r
import schedule

from Symbol import Stock


class IEX_Symbol:
    """
    Functions for finding stock market information about symbols.
    """

    SYMBOL_REGEX = "[$]([a-zA-Z]{1,4})"

    searched_symbols = {}
    otc_list = []
    charts = {}
    trending_cache = None

    def __init__(self) -> None:
        """Creates a Symbol Object

        Parameters
        ----------
        IEX_TOKEN : str
            IEX API Token
        """
        try:
            self.IEX_TOKEN = os.environ["IEX"]

            if self.IEX_TOKEN == "TOKEN":
                self.IEX_TOKEN = ""
        except KeyError:
            self.IEX_TOKEN = ""
            warning(
                "Starting without an IEX Token will not allow you to get market data!"
            )

        if self.IEX_TOKEN != "":
            self.get_symbol_list()

            schedule.every().day.do(self.get_symbol_list)
            schedule.every().day.do(self.clear_charts)

    def get(self, endpoint, params: dict = {}, timeout=5) -> dict:

        url = "https://cloud.iexapis.com/stable" + endpoint

        # set token param if it wasn't passed.
        params["token"] = params.get("token", self.IEX_TOKEN)

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

            # IEX uses backtick ` as apostrophe which breaks telegram markdown parsing
            if type(resp_json) is dict:
                resp_json["companyName"] = resp_json.get("companyName", "").replace(
                    "`", "'"
                )

            return resp_json
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

    def get_symbol_list(
        self, return_df=False
    ) -> Optional[Tuple[pd.DataFrame, datetime]]:
        """Gets list of all symbols supported by IEX

        Parameters
        ----------
        return_df : bool, optional
            return the dataframe of all stock symbols, by default False

        Returns
        -------
        Optional[Tuple[pd.DataFrame, datetime]]
            If `return_df` is set to `True` returns a dataframe, otherwise returns `None`.
        """

        reg_symbols = self.get("/ref-data/symbols")
        otc_symbols = self.get("/ref-data/otc/symbols")

        reg = pd.DataFrame(data=reg_symbols)
        otc = pd.DataFrame(data=otc_symbols)
        self.otc_list = set(otc["symbol"].to_list())

        symbols = pd.concat([reg, otc])

        # IEX uses backtick ` as apostrophe which breaks telegram markdown parsing
        symbols["name"] = symbols["name"].str.replace("`", "'")

        symbols["description"] = "$" + symbols["symbol"] + ": " + symbols["name"]
        symbols["id"] = symbols["symbol"]
        symbols["type_id"] = "$" + symbols["symbol"].str.lower()

        symbols = symbols[["id", "symbol", "name", "description", "type_id"]]
        self.symbol_list = symbols
        if return_df:
            return symbols, datetime.now()

    def status(self) -> str:
        """Checks IEX Status dashboard for any current API issues.

        Returns
        -------
        str
            Human readable text on status of IEX API
        """

        if self.IEX_TOKEN == "":
            return "The `IEX_TOKEN` is not set so Stock Market data is not available."

        resp = r.get(
            "https://pjmps0c34hp7.statuspage.io/api/v2/status.json",
            timeout=15,
        )

        if resp.status_code == 200:
            status = resp.json()["status"]
        else:
            return "IEX Cloud did not respond. Please check their status page for more information. https://status.iexapis.com"

        if status["indicator"] == "none":
            return "IEX Cloud is currently not reporting any issues with its API."
        else:
            return (
                f"{status['indicator']}: {status['description']}."
                + " Please check the status page for more information. https://status.iexapis.com"
            )

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

        if IEXData := self.get(f"/stock/{symbol.id}/quote"):

            if symbol.symbol.upper() in self.otc_list:
                return f"OTC - {symbol.symbol.upper()}, {IEXData['companyName']} most recent price is: $**{IEXData['latestPrice']}**"

            keys = (
                "extendedChangePercent",
                "extendedPrice",
                "companyName",
                "latestPrice",
                "changePercent",
            )

            if set(keys).issubset(IEXData):

                if change := IEXData.get("changePercent", 0):
                    change = round(change * 100, 2)
                else:
                    change = 0

                if (
                    IEXData.get("isUSMarketOpen", True)
                    or (IEXData["extendedChangePercent"] is None)
                    or (IEXData["extendedPrice"] is None)
                ):  # Check if market is open.
                    message = f"The current stock price of {IEXData['companyName']} is $**{IEXData['latestPrice']}**"
                else:
                    message = (
                        f"{IEXData['companyName']} closed at $**{IEXData['latestPrice']}** with a change of {change}%,"
                        + f" after hours _(15 minutes delayed)_ the stock price is $**{IEXData['extendedPrice']}**"
                    )
                    if change := IEXData.get("extendedChangePercent", 0):
                        change = round(change * 100, 2)
                    else:
                        change = 0

                # Determine wording of change text
                if change > 0:
                    message += f", the stock is currently **up {change}%**"
                elif change < 0:
                    message += f", the stock is currently **down {change}%**"
                else:
                    message += ", the stock hasn't shown any movement today."
            else:
                message = (
                    f"The symbol: {symbol} encountered and error. This could be due to "
                )

        else:
            message = f"The symbol: {symbol} was not found."

        return message

    def dividend_reply(self, symbol: Stock) -> str:
        """Returns the most recent, or next dividend date for a stock symbol.

        Parameters
        ----------
        symbol : Stock

        Returns
        -------
        str
            Formatted markdown
        """
        if symbol.symbol.upper() in self.otc_list:
            return "OTC stocks do not currently support any commands."

        if resp := self.get(f"/stock/{symbol.id}/dividends/next"):
            try:
                IEXData = resp[0]
            except IndexError as e:
                logging.info(e)
                return f"Getting dividend information for ${symbol.id.upper()} encountered an error. The provider for upcoming dividend information has been having issues recently which has likely caused this error. It is also possible that the stock has no dividend or does not exist."
            keys = (
                "amount",
                "currency",
                "declaredDate",
                "exDate",
                "frequency",
                "paymentDate",
                "flag",
            )

            if set(keys).issubset(IEXData):

                if IEXData["currency"] == "USD":
                    price = f"${IEXData['amount']}"
                else:
                    price = f"{IEXData['amount']} {IEXData['currency']}"

                # Pattern IEX uses for dividend date.
                pattern = "%Y-%m-%d"

                declared = datetime.strptime(IEXData["declaredDate"], pattern).strftime(
                    "%A, %B %w"
                )
                ex = datetime.strptime(IEXData["exDate"], pattern).strftime("%A, %B %w")
                payment = datetime.strptime(IEXData["paymentDate"], pattern).strftime(
                    "%A, %B %w"
                )

                daysDelta = (
                    datetime.strptime(IEXData["paymentDate"], pattern) - datetime.now()
                ).days

                return (
                    "The next dividend for "
                    + f"{self.symbol_list[self.symbol_list['symbol']==symbol.id.upper()]['description'].item()}"  # Get full name without api call
                    + f" is on {payment} which is in {daysDelta} days."
                    + f" The dividend is for {price} per share."
                    + f"\n\nThe dividend was declared on {declared} and the ex-dividend date is {ex}"
                )

        return f"Getting dividend information for ${symbol.id.upper()} encountered an error. The provider for upcoming dividend information has been having issues recently which has likely caused this error. It is also possible that the stock has no dividend or does not exist."

    def news_reply(self, symbol: Stock) -> str:
        """Gets most recent, english, non-paywalled news

        Parameters
        ----------
        symbol : Stock

        Returns
        -------
        str
            Formatted markdown
        """
        if symbol.symbol.upper() in self.otc_list:
            return "OTC stocks do not currently support any commands."

        if data := self.get(f"/stock/{symbol.id}/news/last/15"):
            line = []

            for news in data:
                if news["lang"] == "en" and not news["hasPaywall"]:
                    line.append(
                        f"*{news['source']}*: [{news['headline']}]({news['url']})"
                    )

            return f"News for **{symbol.id.upper()}**:\n" + "\n".join(line[:5])

        else:
            return f"No news found for: {symbol.id}\nEither today is boring or the symbol does not exist."

    def info_reply(self, symbol: Stock) -> str:
        """Gets description for Stock

        Parameters
        ----------
        symbol : Stock

        Returns
        -------
        str
            Formatted text
        """
        if symbol.symbol.upper() in self.otc_list:
            return "OTC stocks do not currently support any commands."

        if data := self.get(f"/stock/{symbol.id}/company"):
            [data.pop(k) for k in list(data) if data[k] == ""]

            if "description" in data:
                return data["description"]

        return f"No information found for: {symbol}\nEither today is boring or the symbol does not exist."

    def stat_reply(self, symbol: Stock) -> str:
        """Key statistics on a Stock

        Parameters
        ----------
        symbol : Stock

        Returns
        -------
        str
            Formatted markdown
        """
        if symbol.symbol.upper() in self.otc_list:
            return "OTC stocks do not currently support any commands."

        if data := self.get(f"/stock/{symbol.id}/stats"):
            [data.pop(k) for k in list(data) if data[k] == ""]

            m = ""
            if "companyName" in data:
                m += f"Company Name: {data['companyName']}\n"
            if "marketcap" in data:
                m += f"Market Cap: ${data['marketcap']:,}\n"
            if "week52high" in data:
                m += f"52 Week (high-low): {data['week52high']:,} "
            if "week52low" in data:
                m += f"- {data['week52low']:,}\n"
            if "employees" in data:
                m += f"Number of Employees: {data['employees']:,}\n"
            if "nextEarningsDate" in data:
                m += f"Next Earnings Date: {data['nextEarningsDate']}\n"
            if "peRatio" in data:
                m += f"Price to Earnings: {data['peRatio']:.3f}\n"
            if "beta" in data:
                m += f"Beta: {data['beta']:.3f}\n"
            return m
        else:
            return f"No information found for: {symbol}\nEither today is boring or the symbol does not exist."

    def cap_reply(self, symbol: Stock) -> str:
        """Get the Market Cap of a stock"""

        if data := self.get(f"/stock/{symbol.id}/stats"):

            try:
                cap = data["marketcap"]
            except KeyError:
                return f"{symbol.id} returned an error."

            message = f"The current market cap of {symbol.name} is $**{cap:,.2f}**"

        else:
            message = f"The Stock: {symbol.name} was not found or returned and error."

        return message

    def intra_reply(self, symbol: Stock) -> pd.DataFrame:
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
        if symbol.symbol.upper() in self.otc_list:
            return pd.DataFrame()

        if symbol.id.upper() not in list(self.symbol_list["symbol"]):
            return pd.DataFrame()

        if data := self.get(f"/stock/{symbol.id}/intraday-prices"):
            df = pd.DataFrame(data)
            df.dropna(inplace=True, subset=["date", "minute", "high", "low", "volume"])
            df["DT"] = pd.to_datetime(df["date"] + "T" + df["minute"])
            df = df.set_index("DT")
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

        if symbol.symbol.upper() in self.otc_list:
            return pd.DataFrame()

        if symbol.id.upper() not in list(self.symbol_list["symbol"]):
            return pd.DataFrame()

        try:  # https://stackoverflow.com/a/3845776/8774114
            return self.charts[symbol.id.upper()]
        except KeyError:
            pass

        if data := self.get(
            f"/stock/{symbol.id}/chart/1mm",
            params={"chartInterval": 3, "includeToday": "false"},
        ):
            df = pd.DataFrame(data)
            df.dropna(inplace=True, subset=["date", "minute", "high", "low", "volume"])
            df["DT"] = pd.to_datetime(df["date"] + "T" + df["minute"])
            df = df.set_index("DT")
            self.charts[symbol.id.upper()] = df
            return df

        return pd.DataFrame()

    def spark_reply(self, symbol: Stock) -> str:
        quote = self.get(f"/stock/{symbol.id}/quote")

        open_change = quote.get("changePercent", 0)
        after_change = quote.get("extendedChangePercent", 0)

        change = 0

        if open_change:
            change = change + open_change
        if after_change:
            change = change + after_change

        change = change * 100

        return f"`{symbol.tag}`: {quote['companyName']}, {change:.2f}%"

    def trending(self) -> list[str]:
        """Gets current coins trending on IEX. Only returns when market is open.

        Returns
        -------
        list[str]
            list of $ID: NAME, CHANGE%
        """

        if data := self.get(f"/stock/market/list/mostactive"):
            self.trending_cache = [
                f"`${s['symbol']}`: {s['companyName']}, {100*s['changePercent']:.2f}%"
                for s in data
            ]

        return self.trending_cache

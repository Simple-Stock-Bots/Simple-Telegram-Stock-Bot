"""Class with functions for running the bot with IEX Cloud.
"""

from datetime import datetime
from typing import Optional, List, Tuple

import pandas as pd
import requests as r
import schedule
from fuzzywuzzy import fuzz
import os

from Symbol import Stock


class IEX_Symbol:
    """
    Functions for finding stock market information about symbols.
    """

    SYMBOL_REGEX = "[$]([a-zA-Z]{1,4})"

    searched_symbols = {}
    charts = {}

    def __init__(self) -> None:
        """Creates a Symbol Object

        Parameters
        ----------
        IEX_TOKEN : str
            IEX Token
        """
        try:
            self.IEX_TOKEN = os.environ["IEX"]
        except KeyError:
            self.IEX_TOKEN = ""
            print(
                "Starting without an IEX Token will not allow you to get market data!"
            )

        if self.IEX_TOKEN != "":
            self.get_symbol_list()

            schedule.every().day.do(self.get_symbol_list)
            schedule.every().day.do(self.clear_charts)

    def clear_charts(self) -> None:
        """Clears cache of chart data."""
        self.charts = {}

    def get_symbol_list(
        self, return_df=False
    ) -> Optional[Tuple[pd.DataFrame, datetime]]:

        reg_symbols = r.get(
            f"https://cloud.iexapis.com/stable/ref-data/symbols?token={self.IEX_TOKEN}"
        ).json()
        otc_symbols = r.get(
            f"https://cloud.iexapis.com/stable/ref-data/otc/symbols?token={self.IEX_TOKEN}"
        ).json()

        reg = pd.DataFrame(data=reg_symbols)
        otc = pd.DataFrame(data=otc_symbols)

        symbols = pd.concat([reg, otc])

        symbols["description"] = "$" + symbols["symbol"] + ": " + symbols["name"]
        symbols["id"] = symbols["symbol"]

        symbols = symbols[["id", "symbol", "name", "description"]]
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
        resp = r.get("https://pjmps0c34hp7.statuspage.io/api/v2/status.json")

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

    def search_symbols(self, search: str) -> List[Tuple[str, str]]:
        """Performs a fuzzy search to find stock symbols closest to a search term.

        Parameters
        ----------
        search : str
            String used to search, could be a company name or something close to the companies stock ticker.

        Returns
        -------
        List[tuple[str, str]]
            A list tuples of every stock sorted in order of how well they match. Each tuple contains: (Symbol, Issue Name).
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

    def price_reply(self, symbol: Stock) -> str:
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

        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol.id}/quote?token={self.IEX_TOKEN}"

        response = r.get(IEXurl)
        if response.status_code == 200:
            IEXData = response.json()
            keys = (
                "extendedChangePercent",
                "extendedPrice",
                "companyName",
                "latestPrice",
                "changePercent",
            )

            if set(keys).issubset(IEXData):



                if (
                    IEXData.get("isUSMarketOpen", True)
                    or (IEXData["extendedChangePercent"] is None)
                    or (IEXData["extendedPrice"] is None)
                ):  # Check if market is open.
                    message = f"The current stock price of {IEXData['companyName']} is $**{IEXData['latestPrice']}**"

                else:
                    message = (
                        f"{IEXData['companyName']} closed at $**{IEXData['latestPrice']}**,"
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
        symbols : list
            List of stock symbols.

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable formatted string of the symbols div dates.
        """

        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/dividends/next?token={self.IEX_TOKEN}"
        response = r.get(IEXurl)
        if response.status_code == 200 and response.json():
            IEXData = response.json()[0]
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
                    "The next dividend for"
                    + f"${self.symbol_list[self.symbol_list['symbol']==symbol.id.upper()]['description'].item()}"
                    + f" is on {payment} which is in {daysDelta} days."
                    + f" The dividend is for {price} per share."
                    + f"\nThe dividend was declared on {declared} and the ex-dividend date is {ex}"
                )

        return f"{symbol} either doesn't exist or pays no dividend."

    def news_reply(self, symbol: Stock) -> str:
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

        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/news/last/5?token={self.IEX_TOKEN}"
        response = r.get(IEXurl)
        if response.status_code == 200:
            data = response.json()
            if len(data):
                message = f"News for **{symbol.id.upper()}**:\n\n"
                for news in data:
                    if news["lang"] == "en" and not news["hasPaywall"]:
                        message = (
                            f"*{news['source']}*: [{news['headline']}]({news['url']})\n"
                        )
                        message += message
            else:
                return f"No news found for: {symbol}\nEither today is boring or the symbol does not exist."
        else:
            return f"No news found for: {symbol}\nEither today is boring or the symbol does not exist."

        return message

    def info_reply(self, symbol: Stock) -> str:
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

        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/company?token={self.IEX_TOKEN}"
        response = r.get(IEXurl)

        if response.status_code == 200:
            data = response.json()
            message = (
                f"Company Name: [{data['companyName']}]({data['website']})\nIndustry:"
                + f" {data['industry']}\nSector: {data['sector']}\nCEO: {data['CEO']}\nDescription: {data['description']}\n"
            )

        else:
            message = f"No information found for: {symbol}\nEither today is boring or the symbol does not exist."

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
        if symbol.id.upper() not in list(self.symbol_list["symbol"]):
            return pd.DataFrame()

        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/intraday-prices?token={self.IEX_TOKEN}"
        response = r.get(IEXurl)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
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

        if symbol.id.upper() not in list(self.symbol_list["symbol"]):
            return pd.DataFrame()

        try:  # https://stackoverflow.com/a/3845776/8774114
            return self.charts[symbol.id.upper()]
        except KeyError:
            pass

        response = r.get(
            f"https://cloud.iexapis.com/stable/stock/{symbol}/chart/1mm?token={self.IEX_TOKEN}&chartInterval=3&includeToday=false"
        )

        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            df.dropna(inplace=True, subset=["date", "minute", "high", "low", "volume"])
            df["DT"] = pd.to_datetime(df["date"] + "T" + df["minute"])
            df = df.set_index("DT")
            self.charts[symbol.id.upper()] = df
            return df

        return pd.DataFrame()

    def stat_reply(self, symbol: Stock) -> str:
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

        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/stats?token={self.IEX_TOKEN}"
        response = r.get(IEXurl)

        if response.status_code == 200:
            data = response.json()
            [data.pop(k) for k in list(data) if data[k] == ""]

            m = ""
            if "companyName" in data:
                m += f"Company Name: {data['companyName']}\n"
            if "marketcap" in data:
                m += f"Market Cap: {data['marketcap']:,}\n"
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

    def trending(self) -> list[str]:
        """Gets current coins trending on coingecko

        Returns
        -------
        list[str]
            list of $$ID: NAME
        """

        stocks = r.get(
            f"https://cloud.iexapis.com/stable/stock/market/list/mostactive?token={self.IEX_TOKEN}"
        ).json()

        return [f"${s['symbol']}: {s['companyName']}" for s in stocks]
import json
import os
import re
from datetime import datetime, timedelta

import pandas as pd
import requests as r
import schedule
from fuzzywuzzy import fuzz


class Symbol:
    """
    Functions for finding stock market information about symbols.
    """

    SYMBOL_REGEX = "[$]([a-zA-Z]{1,4})"

    searched_symbols = {}

    help_text = """
Thanks for using this bot, consider supporting it by [buying me a beer.](https://www.buymeacoffee.com/Anson)

Full documentation can be found [here.](https://simple-stock-bots.gitlab.io/site)

**Commands**
    - /dividend `$[symbol]` will return dividend information for the symbol.
    - /news `$[symbol]` will return news about the symbol.
    - /info `$[symbol]` will return general information about the symbol.

**Inline Features**
    You can type @SimpleStockBot `[search]` in any chat or direct message to search for the stock bots full list of stock symbols and return the price of the ticker. 

The bot also looks at every message in any chat it is in for stock symbols. Symbols start with a `$` followed by the stock symbol. For example: $tsla would return price information for Tesla Motors. 

Market data is provided by [IEX Cloud](https://iexcloud.io)
    """

    def __init__(self, IEX_TOKEN: str):
        self.IEX_TOKEN = IEX_TOKEN
        self.get_symbol_list()
        schedule.every().day.do(self.get_symbol_list)

    def get_symbol_list(self, return_df=False):
        """
        Fetches a list of stock market symbols from FINRA
        
        Returns:
            pd.DataFrame -- [DataFrame with columns: Symbol | Issue_Name | Primary_Listing_Mkt
            datetime -- The time when the list of symbols was fetched. The Symbol list is updated every open and close of every trading day. 
        """
        raw_symbols = r.get(
            f"https://cloud.iexapis.com/stable/ref-data/symbols?token={self.IEX_TOKEN}"
        ).json()
        symbols = pd.DataFrame(data=raw_symbols)

        symbols["description"] = symbols["symbol"] + ": " + symbols["name"]
        self.symbol_list = symbols
        if return_df:
            return symbols, datetime.now()

    def search_symbols(self, search: str):
        """
        Performs a fuzzy search to find stock symbols closest to a search term.
        
        Arguments:
            search {str} -- String used to search, could be a company name or something close to the companies stock ticker.
        
        Returns:
            List of Tuples -- A list tuples of every stock sorted in order of how well they match. Each tuple contains: (Symbol, Issue Name).
        """
        schedule.run_pending()
        search = search.lower()
        try:  # https://stackoverflow.com/a/3845776/8774114
            return self.searched_symbols[search]
        except KeyError:
            pass

        symbols = self.symbol_list
        symbols["Match"] = symbols.apply(
            lambda x: fuzz.ratio(search, f"{x['symbol']}".lower()), axis=1,
        )

        symbols.sort_values(by="Match", ascending=False, inplace=True)
        if symbols["Match"].head().sum() < 300:
            symbols["Match"] = symbols.apply(
                lambda x: fuzz.partial_ratio(search, x["name"].lower()), axis=1,
            )

            symbols.sort_values(by="Match", ascending=False, inplace=True)
        symbols = symbols.head(10)
        symbol_list = list(zip(list(symbols["symbol"]), list(symbols["description"])))
        self.searched_symbols[search] = symbol_list
        return symbol_list

    def find_symbols(self, text: str):
        """
        Finds stock tickers starting with a dollar sign in a blob of text and returns them in a list. Only returns each match once. Example: Whats the price of $tsla? -> ['tsla']
        
        Arguments:
            text {str} -- Blob of text that might contain tickers with the format: $TICKER
        
        Returns:
            list -- List of every found match without the dollar sign. 
        """

        return list(set(re.findall(self.SYMBOL_REGEX, text)))

    def price_reply(self, symbols: list):
        """
        Takes a list of symbols and replies with Markdown formatted text about the symbols price change for the day.
        
        Arguments:
            symbols {list} -- List of stock market symbols.
        
        Returns:
            dict -- Dictionary with keys of symbols and values of markdown formatted text example: {'tsla': 'The current stock price of Tesla Motors is $**420$$, the stock price is currently **up 42%**}
        """
        dataMessages = {}
        for symbol in symbols:
            IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.IEX_TOKEN}"

            response = r.get(IEXurl)
            if response.status_code == 200:
                IEXData = response.json()
                message = f"The current stock price of {IEXData['companyName']} is $**{IEXData['latestPrice']}**"
                # Determine wording of change text
                change = round(IEXData["changePercent"] * 100, 2)
                if change > 0:
                    message += f", the stock is currently **up {change}%**"
                elif change < 0:
                    message += f", the stock is currently **down {change}%**"
                else:
                    message += ", the stock hasn't shown any movement today."
            else:
                message = f"The symbol: {symbol} was not found."

            dataMessages[symbol] = message

        return dataMessages

    def dividend_reply(self, symbols: list):
        divMessages = {}

        for symbol in symbols:
            IEXurl = f"https://cloud.iexapis.com/stable/data-points/{symbol}/NEXTDIVIDENDDATE?token={self.IEX_TOKEN}"
            response = r.get(IEXurl)
            if response.status_code == 200:

                # extract date from json
                date = response.json()
                # Pattern IEX uses for dividend date.
                pattern = "%Y-%m-%d"
                divDate = datetime.strptime(date, pattern)

                daysDelta = (divDate - datetime.now()).days
                datePretty = divDate.strftime("%A, %B %w")
                if daysDelta < 0:
                    divMessages[
                        symbol
                    ] = f"{symbol.upper()} dividend was on {datePretty} and a new date hasn't been announced yet."
                elif daysDelta > 0:
                    divMessages[
                        symbol
                    ] = f"{symbol.upper()} dividend is on {datePretty} which is in {daysDelta} Days."
                else:
                    divMessages[symbol] = f"{symbol.upper()} is today."

            else:
                divMessages[
                    symbol
                ] = f"{symbol} either doesn't exist or pays no dividend."

        return divMessages

    def news_reply(self, symbols: list):
        newsMessages = {}

        for symbol in symbols:
            IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/news/last/3?token={self.IEX_TOKEN}"
            response = r.get(IEXurl)
            if response.status_code == 200:
                data = response.json()
                newsMessages[symbol] = f"News for **{symbol.upper()}**:\n"
                for news in data:
                    message = f"\t[{news['headline']}]({news['url']})\n\n"
                    newsMessages[symbol] = newsMessages[symbol] + message
            else:
                newsMessages[
                    symbol
                ] = f"No news found for: {symbol}\nEither today is boring or the symbol does not exist."

        return newsMessages

    def info_reply(self, symbols: list):
        infoMessages = {}

        for symbol in symbols:
            IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/company?token={self.IEX_TOKEN}"
            response = r.get(IEXurl)

            if response.status_code == 200:
                data = response.json()
                infoMessages[
                    symbol
                ] = f"Company Name: [{data['companyName']}]({data['website']})\nIndustry: {data['industry']}\nSector: {data['sector']}\nCEO: {data['CEO']}\nDescription: {data['description']}\n"

            else:
                infoMessages[
                    symbol
                ] = f"No information found for: {symbol}\nEither today is boring or the symbol does not exist."

        return infoMessages

    def historical_reply(self, symbol: str, period: str):
        if symbol.upper() not in list(self.symbol_list["symbol"]):
            return pd.DataFrame()

        time_periods = ["max", "5y", "2y", "1y", "ytd", "6m", "3m", "1m", "5d"]
        if period not in time_periods:
            return pd.DataFrame()

        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/chart/{period}?token={self.IEX_TOKEN}"
        response = r.get(IEXurl)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
            return df

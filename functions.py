import json
import os
import re
from datetime import datetime, timedelta

import pandas as pd
import requests as r
from fuzzywuzzy import fuzz


class Symbol:
    SYMBOL_REGEX = "[$]([a-zA-Z]{1,4})"
    LIST_URL = "http://oatsreportable.finra.org/OATSReportableSecurities-SOD.txt"

    def __init__(self, IEX_TOKEN: str):
        self.IEX_TOKEN = IEX_TOKEN
        self.symbol_list, self.symbol_ts = self.get_symbol_list()

    def get_symbol_list(self):
        raw_symbols = r.get(self.LIST_URL).text
        symbols = pd.DataFrame(
            [line.split("|") for line in raw_symbols.split("\n")][:-1]
        )
        symbols.columns = symbols.iloc[0]
        symbols = symbols.drop(symbols.index[0])
        symbols = symbols.drop(symbols.index[-1])
        symbols["Description"] = symbols["Symbol"] + ": " + symbols["Issue_Name"]
        return symbols, datetime.now()

    def search_symbols(self, search: str):
        if self.symbol_ts - datetime.now() > timedelta(hours=12):
            self.symbol_list, self.symbol_ts = self.get_symbol_list()

        symbols = self.symbol_list
        symbols["Match"] = symbols.apply(
            lambda x: fuzz.partial_ratio(
                search.lower(), f"{x['Symbol']} {x['Issue_Name']}".lower()
            ),
            axis=1,
        )
        symbols.sort_values(by="Match", ascending=False, inplace=True)
        return list(zip(list(symbols["Symbol"]), list(symbols["Description"])))

    def find_symbols(self, text: str):
        """
        Takes a blob of text and returns a list of symbols without any repeats.
        """

        return list(set(re.findall(self.SYMBOL_REGEX, text)))

    def price_reply(self, symbols: list):
        """
        Takes a list of symbols and returns a dictionary of strings with information about the symbol.
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

    def symbol_name(self, symbols: list):
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

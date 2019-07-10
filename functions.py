import json
import os
import re
from datetime import datetime

import requests

IEX_TOKEN = os.environ["IEX"]


def getSymbols(text: str):
    """
    Takes a blob of text and returns a list of symbols without any repeats.
    """

    SYMBOL_REGEX = "[$]([a-zA-Z]{1,4})"

    return list(set(re.findall(SYMBOL_REGEX, text)))


def symbolDataReply(symbols: list):
    """
    Takes a list of symbols and returns a dictionary of strings with information about the symbol.
    """
    dataMessages = {}
    for symbol in symbols:
        IEXurl = (
            f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={IEX_TOKEN}"
        )

        response = requests.get(IEXurl)
        if response.status_code is 200:
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


def symbolDividend(symbols: list):
    divMessages = {}

    for symbol in symbols:
        IEXurl = f"https://cloud.iexapis.com/stable/data-points/{symbol}/NEXTDIVIDENDDATE?token={IEX_TOKEN}"
        response = requests.get(IEXurl)
        if response.status_code is 200:

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
            divMessages[symbol] = f"{symbol} either doesn't exist or pays no dividend."

    return divMessages


def symbolNews(symbols: list):
    newsMessages = {}

    for symbol in symbols:
        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/news/last/3?token={IEX_TOKEN}"
        response = requests.get(IEXurl)
        if response.status_code is 200:
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


def symbolInfo(symbols: list):
    infoMessages = {}

    for symbol in symbols:
        IEXurl = (
            f"https://cloud.iexapis.com/stable/stock/{symbol}/company?token={IEX_TOKEN}"
        )
        response = requests.get(IEXurl)

        if response.status_code is 200:
            data = response.json()
            infoMessages[
                symbol
            ] = f"Company Name: [{data['companyName']}]({data['website']})\nIndustry: {data['industry']}\nSector: {data['sector']}\nCEO: {data['CEO']}\nDescription: {data['description']}\n"

        else:
            infoMessages[
                symbol
            ] = f"No information found for: {symbol}\nEither today is boring or the symbol does not exist."

    return infoMessages


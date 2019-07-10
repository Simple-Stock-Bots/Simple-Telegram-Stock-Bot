import json
import os
import re
import urllib.request
import requests
from datetime import datetime

IEX_TOKEN = "sk_130b8e8f75ba4e14a5683ff37a655584"  # os.environ["IEX"]


def getSymbols(text: str):
    """
    Takes a blob of text and returns any stock symbols found.
    """

    SYMBOL_REGEX = "[$]([a-zA-Z]{1,4})"

    return list(set(re.findall(SYMBOL_REGEX, text)))


def symbolDataReply(symbols: list):
    """
    Takes a list of symbols and returns a list of strings with information about the symbol.
    """
    symbolReplies = {}
    for symbol in symbols:
        IEXURL = (
            f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={IEX_TOKEN}"
        )
        try:
            with urllib.request.urlopen(IEXURL) as url:
                IEXData = json.loads(url.read().decode())

            reply = f"The current stock price of {IEXData['companyName']} is $**{IEXData['latestPrice']}**"

            # Determine wording of change text
            change = round(IEXData["changePercent"] * 100, 2)
            if change > 0:
                reply += f", the stock is currently **up {change}%**"
            elif change < 0:
                reply += f", the stock is currently **down {change}%**"
            else:
                reply += ", the stock hasn't shown any movement today."
        except:
            reply = f"The symbol: {symbol} was not found."

        symbolReplies[symbol] = reply

    return symbolReplies


def symbolDividend(symbols: list):
    messages = {}

    for symbol in symbols:
        IEXurl = f"https://cloud.iexapis.com/stable/data-points/{symbol}/NEXTDIVIDENDDATE?token={IEX_TOKEN}"
        response = requests.get(IEXurl)
        if response.status_code is 200:

            date = response.json()
            # Pattern IEX uses for dividend date.
            pattern = "%Y-%m-%d"
            divDate = datetime.strptime(date, pattern)
            #
            daysDelta = (divDate - datetime.now()).days
            datePretty = divDate.strftime("%A, %B %w")
            if daysDelta < 0:
                messages[
                    symbol
                ] = f"{symbol.upper()} dividend was on {datePretty} and a new date hasn't been announced yet."
            elif daysDelta > 0:
                messages[
                    symbol
                ] = f"{symbol.upper()} dividend is on {datePretty} which is in {daysDelta} Days."
            else:
                messages[symbol] = f"{symbol.upper()} is today."

        else:
            messages[symbol] = f"{symbol} either doesn't exist or pays no dividend."

    return messages


def symbolNews(symbols: list):
    messages = {}

    for symbol in symbols:
        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/news/last/3?token={IEX_TOKEN}"
        with urllib.request.urlopen(IEXurl) as url:
            data = json.loads(url.read().decode())
        if data:
            messages[symbol] = f"News for **{symbol.upper()}**:\n"
            for news in data:
                message = f"\t[{news['headline']}]({news['url']})\n\n"
                messages[symbol] = messages[symbol] + message
        else:
            messages[
                symbol
            ] = f"No news found for: {symbol}\nEither today is boring or the symbol does not exist."

    return messages


def symbolInfo(symbols: list):
    messages = {}

    for symbol in symbols:
        IEXurl = (
            f"https://cloud.iexapis.com/stable/stock/{symbol}/company?token={IEX_TOKEN}"
        )
        with urllib.request.urlopen(IEXurl) as url:
            data = json.loads(url.read().decode())
        if data:
            messages[
                symbol
            ] = f"Company Name: [{data['companyName']}]({data['website']})\nIndustry: {data['industry']}\nSector: {data['sector']}\nCEO: {data['CEO']}\nDescription: {data['description']}\n"

        else:
            messages[
                symbol
            ] = f"No information found for: {symbol}\nEither today is boring or the symbol does not exist."

    return messages


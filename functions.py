import json
import os
import re
import urllib.request
import requests
from datetime import datetime

IEX_TOKEN = os.environ["IEX"]


def getTickers(text: str):
    """
    Takes a blob of text and returns any stock tickers found.
    """

    TICKER_REGEX = "[$]([a-zA-Z]{1,4})"

    return list(set(re.findall(TICKER_REGEX, text)))


def tickerDataReply(tickers: list):
    """
    Takes a list of tickers and returns a list of strings with information about the ticker.
    """
    tickerReplies = {}
    for ticker in tickers:
        IEXURL = (
            f"https://cloud.iexapis.com/stable/stock/{ticker}/quote?token={IEX_TOKEN}"
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
            reply = f"The ticker: {ticker} was not found."

        tickerReplies[ticker] = reply

    return tickerReplies


def tickerDividend(tickers: list):
    messages = {}

    for ticker in tickers:
        IEXurl = f"https://cloud.iexapis.com/stable/data-points/{ticker}/NEXTDIVIDENDDATE?token={IEX_TOKEN}"
        date = requests.get(IEXurl).json()
        if date:
            # Pattern IEX uses for dividend date.
            pattern = "%Y-%m-%d"
            divDate = datetime.strptime(date, pattern)
            #
            daysDelta = divDate - datetime.now()
            datePretty = divDate.strftime("%A, %B %w")

            messages[
                ticker
            ] = f"{ticker.upper()} dividend is on {datePretty} which is in {daysDelta} Days."
        else:
            messages[ticker] = f"{ticker} either doesn't exist or pays no dividend."

    return messages


def tickerNews(tickers: list):
    messages = {}

    for ticker in tickers:
        IEXurl = f"https://cloud.iexapis.com/stable/stock/{ticker}/news/last/3?token={IEX_TOKEN}"
        with urllib.request.urlopen(IEXurl) as url:
            data = json.loads(url.read().decode())
        if data:
            messages[ticker] = f"News for **{ticker.upper()}**:\n"
            for news in data:
                message = f"\t[{news['headline']}]({news['url']})\n\n"
                messages[ticker] = messages[ticker] + message
        else:
            messages[
                ticker
            ] = f"No news found for: {ticker}\nEither today is boring or the ticker does not exist."

    return messages


def tickerInfo(tickers: list):
    messages = {}

    for ticker in tickers:
        IEXurl = (
            f"https://cloud.iexapis.com/stable/stock/{ticker}/company?token={IEX_TOKEN}"
        )
        with urllib.request.urlopen(IEXurl) as url:
            data = json.loads(url.read().decode())
        if data:
            messages[
                ticker
            ] = f"Company Name: [{data['companyName']}]({data['website']})\nIndustry: {data['industry']}\nSector: {data['sector']}\nCEO: {data['CEO']}\nDescription: {data['description']}\n"

        else:
            messages[
                ticker
            ] = f"No information found for: {ticker}\nEither today is boring or the ticker does not exist."

    return messages


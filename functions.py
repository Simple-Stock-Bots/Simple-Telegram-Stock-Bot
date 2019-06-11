import json
import os
import re
import time
import urllib.request
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
        IEXurl = f"https://cloud.iexapis.com/stable/stock/{ticker}/dividends/next?token={IEX_TOKEN}"
        with urllib.request.urlopen(IEXurl) as url:
            data = json.loads(url.read().decode())
        if data:
            # Pattern IEX uses for dividend date.
            pattern = "%Y-%m-%d"

            # Convert divDate to seconds, and subtract it from current time.
            dividendSeconds = datetime.strptime(
                data["paymentDate"], pattern
            ).timestamp()
            difference = dividendSeconds - int(time.time())

            # Calculate (d)ays, (h)ours, (m)inutes, and (s)econds
            d, h = divmod(difference, 86400)
            h, m = divmod(h, 3600)
            m, s = divmod(m, 60)

            messages[
                ticker
            ] = f"{data['description']}\n\nThe dividend is in: {d:.0f} Days {h:.0f} Hours {m:.0f} Minutes {s:.0f} Seconds."
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

import json
import re
import time
import urllib.request
from datetime import datetime

import cred


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
            f"https://cloud.iexapis.com/stable/stock/{ticker}/quote?token={cred.secret}"
        )
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

        tickerReplies[ticker] = reply

    return tickerReplies


# Below Functions are incomplete


def tickerInfo(ticker):
    infoURL = f"https://api.iextrading.com/1.0/stock/{ticker}/stats"

    with urllib.request.urlopen(infoURL) as url:
        data = json.loads(url.read().decode())

    info = {}

    info["companyName"] = data["companyName"]
    info["marketCap"] = data["marketcap"]
    info["yearHigh"] = data["week52high"]
    info["yearLow"] = data["week52low"]
    info["divRate"] = data["dividendRate"]
    info["divYield"] = data["dividendYield"]
    info["divDate"] = data["exDividendDate"]

    return info


def tickerDividend(ticker):
    data = tickerInfo(ticker)
    if data["divDate"] == 0:
        return "{} has no dividend.".format(data["companyName"])

    dividendInfo = "{} current dividend yield is: {:.3f}%, or ${:.3f} per share.".format(
        data["companyName"], data["divRate"], data["divYield"]
    )

    divDate = data["divDate"]

    # Pattern IEX uses for dividend date.
    pattern = "%Y-%m-%d %H:%M:%S.%f"

    # Convert divDate to seconds, and subtract it from current time.
    divSeconds = datetime.strptime(divDate, pattern).timestamp()
    difference = divSeconds - int(time.time())

    # Calculate (d)ays, (h)ours, (m)inutes, and (s)econds
    d, h = divmod(difference, 86400)
    h, m = divmod(h, 3600)
    m, s = divmod(m, 60)

    countdownMessage = f"\n\nThe dividend is in: {d:.0f} Days {h:.0f} Hours {m:.0f} Minutes {s:.0f} Seconds."

    return dividendInfo + countdownMessage

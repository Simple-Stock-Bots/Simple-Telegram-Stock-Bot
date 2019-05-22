import json
import re
import time
import urllib.request
from datetime import datetime


def getTickers(text: str):
    """
    Takes a blob of text and returns any stock tickers found.
    """

    TICKER_REGEX = "[$]([a-zA-Z]{1,4})"

    return list(set(re.findall(TICKER_REGEX, text)))


def tickerData(tickers: list):
    """
    Takes a list of tickers and returns a dictionary of information on ticker.
    example: 
        input list: ["aapl","tsla"]
    returns:
    {
        "AAPL": {"name": "Apple Inc.", "price": 200.72, "change": -0.01074},
        "TSLA": {"name": "Tesla Inc.", "price": 241.98, "change": -0.01168},
    }
    """

    stockData = {}
    IEXURL = (
        "https://api.iextrading.com/1.0/stock/market/batch?symbols="
        + ",".join(tickers)
        + "&types=quote"
    )
    with urllib.request.urlopen(IEXURL) as url:
        IEXData = json.loads(url.read().decode())

    for ticker in tickers:
        ticker = ticker.upper()

        # Makes sure ticker exists before populating a dictionary
        if ticker in IEXData:
            stockData[ticker] = {}
            stockData[ticker]["name"] = IEXData[ticker]["quote"]["companyName"]
            stockData[ticker]["price"] = IEXData[ticker]["quote"]["latestPrice"]
            stockData[ticker]["change"] = IEXData[ticker]["quote"]["changePercent"]

    return stockData


def tickerDataReply(ticker: dict):
    """
    Takes a dictionary, likely produced from tickerData(), and returns a markdown string with information on the ticker.
    example:  
        input dict: {"AAPL": {"name": "Apple Inc.", "price": 200.72, "change": -0.01074}}
    returns:
        The current stock price of Apple Inc. is $**200.72**, the stock is currently **down -1.07**%
    """
    reply = f"The current stock price of {ticker['name']} is $**{ticker['price']}**"

    # Determine wording of change text
    change = round(ticker["change"] * 100, 2)
    if change > 0:
        changeText = f", the stock is currently **up {change}%**"
    elif change < 0:
        changeText = f", the stock is currently **down {change}%**"
    else:
        changeText = ", the stock hasn't shown any movement today."

    return reply + changeText


def tickerNews(tickers: list):
    """
    Takes a list of ticker and returns a dictionary of dictionarys 
    with a list of tuples under news that contains (title, url)
    example:
        input list: ["aapl"]
    returns:
        {
            "AAPL": {
                "name": "Apple Inc.",
                "price": 200.72,
                "change": -0.01074,
                "news": [
                    (
                        "April Dividend Income Report - Beating Records, Holding Steady",
                        "https://api.iextrading.com/1.0/stock/aapl/article/8556681822768653",
                    ),
                    (
                        "Is Vanguard's VIG Better Than Its WisdomTree Counterpart?",
                        "https://api.iextrading.com/1.0/stock/aapl/article/7238581261167527",
                    ),
                ],
            }
        }
    """

    data = tickerData(tickers)

    for ticker in tickers:
        ticker = ticker.upper()
        IEXNews = f"https://api.iextrading.com/1.0/stock/{ticker}/news/last/5"
        with urllib.request.urlopen(IEXNews) as url:
            newsData = json.loads(url.read().decode())

        data[ticker]["news"] = []
        for index, story in enumerate(newsData):
            tup = (newsData[index]["headline"], newsData[index]["url"])
            data[ticker]["news"].append(tup)

    return data


def tickerNewsReply(ticker: dict):
    """
    Takes a dictionary, likely produced from tickerNews(), and returns a markdown string with news information on the ticker.
    example:
        {
            "name": "Apple Inc.",
            "price": 200.72,
            "change": -0.01074,
            "news": [
                (
                    "April Dividend Income Report - Beating Records, Holding Steady",
                    "https://api.iextrading.com/1.0/stock/aapl/article/8556681822768653",
                ),
                (
                    "Is Vanguard's VIG Better Than Its WisdomTree Counterpart?",
                    "https://api.iextrading.com/1.0/stock/aapl/article/7238581261167527",
                ),
            ],
        }
    returns:
        The current stock price of Apple Inc. is $**200.72**, the stock is currently **down -1.07%**
            [April Dividend Income Report - Beating Records, Holding Steady](https://api.iextrading.com/1.0/stock/aapl/article/8556681822768653)
            [Is Vanguard's VIG Better Than Its WisdomTree Counterpart?](https://api.iextrading.com/1.0/stock/aapl/article/7238581261167527)
    """
    reply = tickerDataReply(ticker)
    if len(ticker["news"]) == 0:
        return reply + f"\n\tNo News was found for {ticker['name']}"
    for title, url in ticker["news"]:
        reply = reply + f"\n\t[{title}]({url})"
    return reply


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

import urllib.request
import json
import feedparser
from datetime import datetime
import time


def tickerQuote(tickers):
    """Gathers information from IEX api on stock"""
    stockData = {}
    IEXURL = (
        "https://api.iextrading.com/1.0/stock/market/batch?symbols="
        + ",".join(tickers)
        + "&types=quote"
    )
    print("Gathering Quote from " + IEXURL)
    with urllib.request.urlopen(IEXURL) as url:
        IEXData = json.loads(url.read().decode())

    for ticker in tickers:
        ticker = ticker.upper()

        # Makes sure ticker exists before populating a dictionary
        if ticker in IEXData:
            stockData[ticker] = 1
            stockData[ticker + "Name"] = IEXData[ticker]["quote"]["companyName"]
            stockData[ticker + "Price"] = IEXData[ticker]["quote"]["latestPrice"]
            stockData[ticker + "Change"] = round(
                (IEXData[ticker]["quote"]["changePercent"] * 100), 2
            )
            stockData[ticker + "Image"] = stockLogo(ticker)
            print(ticker + " Quote Gathered")
        else:
            stockData[ticker] = 0
    return stockData


def stockNews(ticker):
    """Makes a bunch of strings that are links to news websites for an input ticker"""
    print("Gather News on " + ticker)

    newsLink = f"https://api.iextrading.com/1.0/stock/{ticker}/news/last/5"

    with urllib.request.urlopen(newsLink) as url:
        data = json.loads(url.read().decode())

    news = {"link": [], "title": []}
    for i in range(3):
        news["link"].append(data[i]["url"])
        news["title"].append(data[i]["headline"])
    return news


def stockLogo(ticker):
    """returns a png of an input ticker"""
    logoURL = f"https://g.foolcdn.com/art/companylogos/mark/{ticker}.png"
    return logoURL


def stockInfo(ticker):
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


def stockDividend(ticker):
    data = stockInfo(ticker)
    print(data["divDate"])
    if data["divDate"] == 0:
        return "{} has no dividend.".format(data["companyName"])

    line1 = "{} current dividend yield is: {:.3f}%, or ${:.3f} per share.".format(
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

    message = line1 + countdownMessage
    return message

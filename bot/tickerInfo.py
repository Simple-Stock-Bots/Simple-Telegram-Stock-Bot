import urllib.request
import json
import feedparser


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

    newsLink = "https://api.iextrading.com/1.0/stock/{}/news/last/5".format(ticker)

    with urllib.request.urlopen(newsLink) as url:
        data = json.loads(url.read().decode())

    news = {"link": [], "title": []}
    for i in range(3):
        news["link"].append(data[i]["url"])
        news["title"].append(data[i]["headline"])
    return news


def stockLogo(ticker):
    """returns a png of an input ticker"""
    logoURL = "https://g.foolcdn.com/art/companylogos/mark/" + ticker + ".png"
    return logoURL

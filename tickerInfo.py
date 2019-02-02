import urllib.request
import json


def tickerQuote(tickers):
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
        stockData[ticker + "Name"] = IEXData[ticker]["quote"]["companyName"]
        stockData[ticker + "Price"] = IEXData[ticker]["quote"]["latestPrice"]
        stockData[ticker + "Change"] = IEXData[ticker]["quote"]["changePercent"] * 100
        stockData[ticker + "Image"] = stockLogo(ticker)
    print("Quote Gathered")
    return stockData


def stockNewsList(ticker):
    print("Gather News on " + ticker)
    news = {
        "Bravos": "https://bravos.co/" + ticker,
        "Seeking Alpha": "https://seekingalpha.com/symbol/" + ticker,
        "MSN Money": "https://www.msn.com/en-us/money/stockdetails?symbol=" + ticker,
        "Yahoo Finance": "https://finance.yahoo.com/quote/" + ticker,
        "Wall Street Journal": "https://quotes.wsj.com/" + ticker,
        "The Street": "https://www.thestreet.com/quote/" + ticker + ".html",
        "Zacks": "https://www.zacks.com/stock/quote/" + ticker,
    }
    print("News gathered.")
    return news


def stockLogo(ticker):
    logoURL = "https://g.foolcdn.com/art/companylogos/mark/" + ticker + ".png"
    return logoURL

import urllib.request
import json


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


def stockNewsList(ticker):
    """Makes a bunch of strings that are links to news websites for an input ticker"""
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
    """returns a png of an input ticker"""
    logoURL = "https://g.foolcdn.com/art/companylogos/mark/" + ticker + ".png"
    return logoURL

import re
from datetime import datetime

import pandas as pd
import requests as r
import schedule
from fuzzywuzzy import fuzz


class Symbol:
    """
    Functions for finding stock market information about symbols.
    """

    SYMBOL_REGEX = "[$]([a-zA-Z]{1,4})"

    searched_symbols = {}
    charts = {}

    license = re.sub(
        r"\b\n",
        " ",
        r.get(
            "https://gitlab.com/simple-stock-bots/simple-telegram-stock-bot/-/raw/master/LICENSE"
        ).text,
    )

    help_text = """
Thanks for using this bot, consider supporting it by [buying me a beer.](https://www.buymeacoffee.com/Anson)

Keep up with the latest news for the bot in itsTelegram Channel: https://t.me/simplestockbotnews

Full documentation on using and running your own stock bot can be found [here.](https://simple-stock-bots.gitlab.io/site)

**Commands**
        - /donate [amount in USD] to donate. 🎗️
        - /dividend $[symbol] will return dividend information for the symbol. 📅
        - /intra $[symbol] Plot of the stocks movement since the last market open.  📈
        - /chart $[symbol] Plot of the stocks movement for the past 1 month. 📊
        - /news $[symbol] News about the symbol. 📰
        - /info $[symbol] General information about the symbol. ℹ️
        - /stat $[symbol] Key statistics about the symbol. 🔢
        - /help Get some help using the bot. 🆘

**Inline Features**
    You can type @SimpleStockBot `[search]` in any chat or direct message to search for the stock bots
    full list of stock symbols and return the price of the ticker. Then once you select the ticker
    want the bot will send a message as you in that chat with the latest stock price.
    The bot also looks at every message in any chat it is in for stock symbols.Symbols start with a
    `$` followed by the stock symbol. For example:$tsla would return price information for Tesla Motors.
    Market data is provided by [IEX Cloud](https://iexcloud.io)

    If you believe the bot is not behaving properly run `/status`.
    """

    donate_text = """
Simple Stock Bot is run entirely on donations[.](https://www.buymeacoffee.com/Anson)
All donations go directly towards paying for servers, and market data is provided by
[IEX Cloud](https://iexcloud.io/).

The easiest way to donate is to run the `/donate [amount in USD]` command with USdollars you would like to donate.

Example: `/donate 2` would donate 2 USD.
An alternative way to donate is through https://www.buymeacoffee.com/Anson,which accepts Paypal or Credit card.
If you have any questions get in touch: @MisterBiggs or[anson@ansonbiggs.com](http://mailto:anson@ansonbiggs.com/)

_Donations can only be made in a chat directly with @simplestockbot_
    """

    def __init__(self, IEX_TOKEN: str):
        self.IEX_TOKEN = IEX_TOKEN
        if IEX_TOKEN != "":
            self.get_symbol_list()

            schedule.every().day.do(self.get_symbol_list)
            schedule.every().day.do(self.clear_charts)

    def clear_charts(self):
        self.charts = {}

    def get_symbol_list(self, return_df=False):
        """
        Fetches a list of stock market symbols from FINRA

        Returns:
            pd.DataFrame -- [DataFrame with columns: Symbol | Issue_Name | Primary_Listing_Mkt
            datetime -- The time when the list of symbols was fetched.

            The Symbol list is updated every open and close of every trading day.
        """
        raw_symbols = r.get(
            f"https://cloud.iexapis.com/stable/ref-data/symbols?token={self.IEX_TOKEN}"
        ).json()
        symbols = pd.DataFrame(data=raw_symbols)

        symbols["description"] = symbols["symbol"] + ": " + symbols["name"]
        self.symbol_list = symbols
        if return_df:
            return symbols, datetime.now()

    def iex_status(self):
        status = r.get("https://pjmps0c34hp7.statuspage.io/api/v2/status.json").json()

        if status["status"]["indicator"] == "none":
            return "IEX Cloud is currently not reporting any issues with its API."
        else:
            return (
                f"{['status']['indicator']}: {['status']['description']}."
                + " Please check the status page for more information. https://status.iexapis.com"
            )

    def message_status(self):
        usage = r.get(
            f"https://cloud.iexapis.com/stable/account/metadata?token={self.IEX_TOKEN}"
        ).json()

        if (
            usage["messagesUsed"] >= usage["messageLimit"] - 10000
            and not usage["payAsYouGoEnabled"]
        ):
            return "Bot may be out of IEX Credits."
        else:
            return "Bot has available IEX Credits"

    def search_symbols(self, search: str):
        """
        Performs a fuzzy search to find stock symbols closest to a search term.

        Arguments:
            search {str} -- String used to search, could be a company name or something close
                to the companies stock ticker.

        Returns:
            List of Tuples -- A list tuples of every stock sorted in order of how well they match.
                Each tuple contains: (Symbol, Issue Name).
        """
        schedule.run_pending()
        search = search.lower()
        try:  # https://stackoverflow.com/a/3845776/8774114
            return self.searched_symbols[search]
        except KeyError:
            pass

        symbols = self.symbol_list
        symbols["Match"] = symbols.apply(
            lambda x: fuzz.ratio(search, f"{x['symbol']}".lower()),
            axis=1,
        )

        symbols.sort_values(by="Match", ascending=False, inplace=True)
        if symbols["Match"].head().sum() < 300:
            symbols["Match"] = symbols.apply(
                lambda x: fuzz.partial_ratio(search, x["name"].lower()),
                axis=1,
            )

            symbols.sort_values(by="Match", ascending=False, inplace=True)
        symbols = symbols.head(10)
        symbol_list = list(zip(list(symbols["symbol"]), list(symbols["description"])))
        self.searched_symbols[search] = symbol_list
        return symbol_list

    def find_symbols(self, text: str):
        """
        Finds stock tickers starting with a dollar sign in a blob of text and returns them in a list.
            Only returns each match once. Example: Whats the price of $tsla? -> ['tsla']

        Arguments:
            text {str} -- Blob of text that might contain tickers with the format: $TICKER

        Returns:
            list -- List of every found match without the dollar sign.
        """

        return list(set(re.findall(self.SYMBOL_REGEX, text)))

    def price_reply(self, symbols: list):
        """
        Takes a list of symbols and replies with Markdown formatted text about the symbols
            price change for the day.

        Arguments:
            symbols {list} -- List of stock market symbols.

        Returns:
            dict -- Dictionary with keys of symbols and values of markdown formatted
                text example: {'tsla': 'The current stock price of Tesla Motors is
                $**420$$, the stock price is currently **up 42%**}
        """
        dataMessages = {}
        for symbol in symbols:
            IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.IEX_TOKEN}"

            response = r.get(IEXurl)
            if response.status_code == 200:
                IEXData = response.json()

                try:  # Some symbols dont return if the market is open
                    IEXData["isUSMarketOpen"]
                except KeyError:
                    IEXData["isUSMarketOpen"] = True

                if (
                    IEXData["isUSMarketOpen"]
                    or (IEXData["extendedChangePercent"] is None)
                    or (IEXData["extendedPrice"] is None)
                ):  # Check if market is open.
                    message = f"The current stock price of {IEXData['companyName']} is $**{IEXData['latestPrice']}**"
                    change = round(IEXData["changePercent"] * 100, 2)
                else:
                    message = (
                        f"{IEXData['companyName']} closed at $**{IEXData['latestPrice']}**,"
                        + " after hours _(15 minutes delayed)_ stock price is $**{IEXData['extendedPrice']}**"
                    )
                    change = round(IEXData["extendedChangePercent"] * 100, 2)

                # Determine wording of change text
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

    def dividend_reply(self, symbols: list):
        divMessages = {}

        for symbol in symbols:
            IEXurl = f"https://cloud.iexapis.com/stable/data-points/{symbol}/NEXTDIVIDENDDATE?token={self.IEX_TOKEN}"
            response = r.get(IEXurl)
            if response.status_code == 200:

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
                divMessages[
                    symbol
                ] = f"{symbol} either doesn't exist or pays no dividend."

        return divMessages

    def news_reply(self, symbols: list):
        newsMessages = {}

        for symbol in symbols:
            IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/news/last/5?token={self.IEX_TOKEN}"
            response = r.get(IEXurl)
            if response.status_code == 200:
                data = response.json()
                if len(data):
                    newsMessages[symbol] = f"News for **{symbol.upper()}**:\n\n"
                    for news in data:
                        if news["lang"] == "en" and not news["hasPaywall"]:
                            message = f"*{news['source']}*: [{news['headline']}]({news['url']})\n"
                            newsMessages[symbol] = newsMessages[symbol] + message
                else:
                    newsMessages[
                        symbol
                    ] = f"No news found for: {symbol}\nEither today is boring or the symbol does not exist."
            else:
                newsMessages[
                    symbol
                ] = f"No news found for: {symbol}\nEither today is boring or the symbol does not exist."

        return newsMessages

    def info_reply(self, symbols: list):
        infoMessages = {}

        for symbol in symbols:
            IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/company?token={self.IEX_TOKEN}"
            response = r.get(IEXurl)

            if response.status_code == 200:
                data = response.json()
                infoMessages[symbol] = (
                    f"Company Name: [{data['companyName']}]({data['website']})\nIndustry:"
                    + " {data['industry']}\nSector: {data['sector']}\nCEO: {data['CEO']}\nDescription: {data['description']}\n"
                )

            else:
                infoMessages[
                    symbol
                ] = f"No information found for: {symbol}\nEither today is boring or the symbol does not exist."

        return infoMessages

    def intra_reply(self, symbol: str):
        if symbol.upper() not in list(self.symbol_list["symbol"]):
            return pd.DataFrame()

        IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/intraday-prices?token={self.IEX_TOKEN}"
        response = r.get(IEXurl)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            df.dropna(inplace=True, subset=["date", "minute", "high", "low", "volume"])
            df["DT"] = pd.to_datetime(df["date"] + "T" + df["minute"])
            df = df.set_index("DT")
            return df

    def chart_reply(self, symbol: str):
        schedule.run_pending()

        if symbol.upper() not in list(self.symbol_list["symbol"]):
            return pd.DataFrame()

        try:  # https://stackoverflow.com/a/3845776/8774114
            return self.charts[symbol.upper()]
        except KeyError:
            pass

        response = r.get(
            "https://cloud.iexapis.com/stable/stock/{symbol}/chart/1mm?token={self.IEX_TOKEN}&chartInterval=3&includeToday=false"
        )

        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            df.dropna(inplace=True, subset=["date", "minute", "high", "low", "volume"])
            df["DT"] = pd.to_datetime(df["date"] + "T" + df["minute"])
            df = df.set_index("DT")
            self.charts[symbol.upper()] = df
            return df

    def stat_reply(self, symbols: list):
        infoMessages = {}

        for symbol in symbols:
            IEXurl = f"https://cloud.iexapis.com/stable/stock/{symbol}/stats?token={self.IEX_TOKEN}"
            response = r.get(IEXurl)

            if response.status_code == 200:
                data = response.json()
                [data.pop(k) for k in list(data) if data[k] == ""]

                m = ""
                if "companyName" in data:
                    m += f"Company Name: {data['companyName']}\n"
                if "marketcap" in data:
                    m += f"Market Cap: {data['marketcap']:,}\n"
                if "week52high" in data:
                    m += f"52 Week (high-low): {data['week52high']:,} "
                if "week52low" in data:
                    m += f"- {data['week52low']:,}\n"
                if "employees" in data:
                    m += f"Number of Employees: {data['employees']:,}\n"
                if "nextEarningsDate" in data:
                    m += f"Next Earnings Date: {data['nextEarningsDate']}\n"
                if "peRatio" in data:
                    m += f"Price to Earnings: {data['peRatio']:.3f}\n"
                if "beta" in data:
                    m += f"Beta: {data['beta']:.3f}\n"
                infoMessages[symbol] = m
            else:
                infoMessages[
                    symbol
                ] = f"No information found for: {symbol}\nEither today is boring or the symbol does not exist."

        return infoMessages

    def crypto_reply(self, pair):
        """Get quote for a cryptocurrency pair.

        Args:
            pair (string): Cryptocurrency
        """

        pair = pair.split(" ")[-1].replace("/", "").upper()
        pair += "USD" if len(pair) == 3 else pair

        IEXurl = f"https://cloud.iexapis.com/stable/crypto/{pair}/quote?token={self.IEX_TOKEN}"

        response = r.get(IEXurl)

        if response.status_code == 200:
            data = response.json()

            quote = f"Symbol: {data['symbol']}\n"
            quote += f"Price: ${data['latestPrice']}\n"

            new, old = data["latestPrice"], data["previousClose"]
            if old is not None:
                change = (float(new) - float(old)) / float(old)
                quote += f"Change: {change}\n"

            return quote

        else:
            return False

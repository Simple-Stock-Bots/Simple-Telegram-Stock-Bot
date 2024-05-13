import datetime as dt
import logging
import os
from collections import OrderedDict
from typing import Dict

import humanize
import pandas as pd
import pytz
import requests as r
import schedule


from common.Symbol import Stock

log = logging.getLogger(__name__)


class MarketData:
    """
    Functions for finding stock market information about symbols from MarkData.app
    """

    SYMBOL_REGEX = "[$]([a-zA-Z]{1,4})"

    symbol_list: Dict[str, Dict] = {}
    charts: Dict[Stock, pd.DataFrame] = {}

    openTime = dt.time(hour=9, minute=30, second=0)
    marketTimeZone = pytz.timezone("US/Eastern")

    def __init__(self) -> None:
        """Creates a Symbol Object

        Parameters
        ----------
        MARKETDATA_TOKEN : str
            MarketData.app API Token
        """

        try:
            self.MARKETDATA_TOKEN = os.environ["MARKETDATA"]

            if self.MARKETDATA_TOKEN == "TOKEN":
                self.MARKETDATA_TOKEN = ""
        except KeyError:
            self.MARKETDATA_TOKEN = ""
            log.warning("Starting without an MarketData.app Token will not allow you to get market data!")
            log.warning("Use this affiliate link so that the bot can stay free:")
            log.warning("https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=repo")

        if self.MARKETDATA_TOKEN != "":
            schedule.every().day.do(self.clear_charts)

        self.get_symbol_list()
        schedule.every().day.do(self.get_symbol_list)

    def get(self, endpoint, params=None, timeout=10, headers=None) -> dict:
        url = "https://api.marketdata.app/v1/" + endpoint

        if params is None:
            params = {}

        # set token param if it wasn't passed.
        params["token"] = self.MARKETDATA_TOKEN

        # Undocumented query variable that ensures bot usage can be
        # monitored even if someone doesn't make it through an affiliate link.
        params["application"] = "simplestockbot"

        if headers is None:
            headers = {}
        headers = {"User-Agent": "Simple Stock Bot anson@ansonbiggs.com"} | headers

        resp = r.get(url, params=params, timeout=timeout, headers=headers)

        logging.error(resp.headers.items())

        # Make sure API returned a proper status code
        try:
            resp.raise_for_status()
        except r.exceptions.HTTPError as e:
            logging.error(e)
            return {}

        # Make sure API returned valid JSON
        try:
            resp_json = resp.json()

            match resp_json["s"]:
                case "ok":
                    return resp_json
                case "no_data":
                    return resp_json
                case "error":
                    logging.error("MarketData Error:\n" + resp_json["errmsg"])
                    return {}

        except r.exceptions.JSONDecodeError as e:
            logging.error(e)

        return {}

    def symbol_id(self, symbol: str) -> Dict[str, Dict]:
        return self.symbol_list.get(symbol.upper(), None)

    def get_symbol_list(self):
        # Doesn't use `self.get()` since needs are much different
        sec_resp = r.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers={
                "User-Agent": "Simple Stock Bot anson@ansonbiggs.com",
                "Accept-Encoding": "gzip, deflate",
                "Host": "www.sec.gov",
            },
        )
        sec_resp.raise_for_status()
        sec_data = sec_resp.json()

        for rank, ticker_info in sec_data.items():
            self.symbol_list[ticker_info["ticker"]] = {
                "ticker": ticker_info["ticker"],
                "title": ticker_info["title"],
                "mkt_cap_rank": rank,
            }

    def clear_charts(self) -> None:
        """
        Clears cache of chart data.
        Charts are cached so that only 1 API call per 24 hours is needed since the
            chart data is expensive and a large download.
        """
        self.charts = {}

    def status(self) -> str:
        # TODO: At the moment this API is poorly documented, this function likely needs to be revisited later.

        try:
            status = r.get(
                "https://stats.uptimerobot.com/api/getMonitorList/6Kv3zIow0A",
                timeout=5,
            )
            status.raise_for_status()
        except r.HTTPError:
            return f"API returned an HTTP error code {status.status_code} in {status.elapsed.total_seconds()} seconds."
        except r.Timeout:
            return "API timed out before it was able to give status. This is likely due to a surge in usage or a complete outage."

        statusJSON = status.json()

        if statusJSON["status"] == "ok":
            return (
                f"CoinGecko API responded that it was OK with a {status.status_code} in {status.elapsed.total_seconds()} seconds."
            )
        else:
            return f"MarketData.app is currently reporting the following status: {statusJSON['status']}"

    def price_reply(self, symbol: Stock) -> str:
        """Returns price movement of Stock for the last market day, or after hours.

        Parameters
        ----------
        symbol : Stock

        Returns
        -------
        str
            Formatted markdown
        """

        if quoteResp := self.get(f"stocks/quotes/{symbol.symbol}/"):
            price = round(quoteResp["last"][0], 2)

            try:
                changePercent = round(quoteResp["changepct"][0], 2)
            except TypeError:
                return f"The price of {symbol.name} is ${price}"

            message = f"The current price of {symbol.name} is ${price} and "

            if changePercent > 0.0:
                message += f"is currently up {changePercent}% for the day."
            elif changePercent < 0.0:
                message += f"is currently down {changePercent}% for the day."
            else:
                message += "hasn't shown any movement for the day."

            return message
        else:
            return f"Getting a quote for {symbol} encountered an error."

    def spark_reply(self, symbol: Stock) -> str:
        if quoteResp := self.get(f"stocks/quotes/{symbol}/"):
            try:
                changePercent = round(quoteResp["changepct"][0], 2)
                return f"`{symbol.tag}`: {changePercent}%"
            except TypeError:
                pass

        return f"`{symbol.tag}`"

    def intra_reply(self, symbol: Stock) -> pd.DataFrame:
        """Returns price data for a symbol of the past month up until the previous trading days close.
        Also caches multiple requests made in the same day.

        Parameters
        ----------
        symbol : str
            Stock symbol.

        Returns
        -------
        pd.DataFrame
            Returns a timeseries dataframe with high, low, and volume data if its available. Otherwise returns empty pd.DataFrame.
        """
        schedule.run_pending()

        try:
            return self.charts[symbol.id.upper()]
        except KeyError:
            pass

        resolution = "15"  # minutes
        now = dt.datetime.now(self.marketTimeZone)

        if self.openTime < now.time():
            startTime = now.replace(hour=9, minute=30)
        else:
            startTime = now - dt.timedelta(days=1)

        if data := self.get(
            f"stocks/candles/{resolution}/{symbol}",
            params={
                "from": startTime.timestamp(),
                "to": now.timestamp(),
                "extended": True,
            },
        ):
            data.pop("s")
            df = pd.DataFrame(data)
            df["t"] = pd.to_datetime(df["t"], unit="s", utc=True)
            df.set_index("t", inplace=True)

            df.rename(
                columns={
                    "o": "Open",
                    "h": "High",
                    "l": "Low",
                    "c": "Close",
                    "v": "Volume",
                },
                inplace=True,
            )

            self.charts[symbol.id.upper()] = df
            return df

        return pd.DataFrame()

    def chart_reply(self, symbol: Stock) -> pd.DataFrame:
        """Returns price data for a symbol of the past month up until the previous trading days close.
        Also caches multiple requests made in the same day.

        Parameters
        ----------
        symbol : str
            Stock symbol.

        Returns
        -------
        pd.DataFrame
            Returns a timeseries dataframe with high, low, and volume data if its available. Otherwise returns empty pd.DataFrame.
        """
        schedule.run_pending()

        try:
            return self.charts[symbol.id.upper()]
        except KeyError:
            pass

        to_date = dt.datetime.today().strftime("%Y-%m-%d")
        from_date = (dt.datetime.today() - dt.timedelta(days=30)).strftime("%Y-%m-%d")
        resultion = "daily"

        if data := self.get(
            f"stocks/candles/{resultion}/{symbol}",
            params={
                "from": from_date,
                "to": to_date,
            },
        ):
            data.pop("s")

            df = pd.DataFrame(data)
            df["t"] = pd.to_datetime(df["t"], unit="s")
            df.set_index("t", inplace=True)

            df.rename(
                columns={
                    "o": "Open",
                    "h": "High",
                    "l": "Low",
                    "c": "Close",
                    "v": "Volume",
                },
                inplace=True,
            )

            self.charts[symbol.id.upper()] = df
            return df

        return pd.DataFrame()

    def options_reply(self, request: str) -> str:
        """Undocumented API Usage!"""

        options_data = self.get(f"options/quotes/{request}")

        for key in options_data.keys():
            options_data[key] = options_data[key][0]

        options_data["underlying"] = "$" + options_data["underlying"]

        options_data["updated"] = humanize.naturaltime(dt.datetime.now() - dt.datetime.fromtimestamp(options_data["updated"]))

        options_data["expiration"] = humanize.naturaltime(
            dt.datetime.now() - dt.datetime.fromtimestamp(options_data["expiration"])
        )

        options_data["firstTraded"] = humanize.naturaltime(
            dt.datetime.now() - dt.datetime.fromtimestamp(options_data["firstTraded"])
        )

        rename = {
            "optionSymbol": "Option Symbol",
            "underlying": "Underlying",
            "expiration": "Expiration",
            "side": "side",
            "strike": "strike",
            "firstTraded": "First Traded",
            "updated": "Last Updated",
            "bid": "bid",
            "bidSize": "bidSize",
            "mid": "mid",
            "ask": "ask",
            "askSize": "askSize",
            "last": "last",
            "openInterest": "Open Interest",
            "volume": "Volume",
            "inTheMoney": "inTheMoney",
            "intrinsicValue": "Intrinsic Value",
            "extrinsicValue": "Extrinsic Value",
            "underlyingPrice": "Underlying Price",
            "iv": "Implied Volatility",
            "delta": "delta",
            "gamma": "gamma",
            "theta": "theta",
            "vega": "vega",
            "rho": "rho",
        }

        options_cleaned = OrderedDict()
        for old, new in rename.items():
            if old in options_data:
                options_cleaned[new] = options_data[old]

        return options_cleaned

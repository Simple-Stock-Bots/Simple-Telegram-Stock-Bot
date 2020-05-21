<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://assets.gitlab-static.net/uploads/-/system/project/avatar/10295651/TelegramLogo.jpg?width=64" alt="Simple Telegram Stock Bot"></a>
</p>

<h3 align="center">Simple Telegram Stock Bot</h3>

<div align="center">
<style>.bmc-button img{height: 34px !important;width: 35px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 35px !important;height:51px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 22px !important;letter-spacing: 0.6px !important;box-shadow: 0px 1px 2px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;margin: 0 auto !important;font-family:'Cookie', cursive !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Cookie" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/Anson"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a beer"><span style="margin-left:5px;font-size:28px !important;">Buy me a beer</span></a>

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Platform](https://img.shields.io/badge/platform-Telegram-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> Telegram Bot 🤖 that provides Stock Market information.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [How it works](#working)
- [Usage](#usage)
- [Getting Started](#getting_started)
- [Deploying your own bot](#deployment)
- [Built Using](#built_using)
- [Contributing](../CONTRIBUTING.md)
- [author](#author)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

This bot aims to be as simple as possible while providing all the information you need on the stock market. The motivation of this bot is to provide similar stock market functionality that the Google Assistant provided in [Google Allo](https://gcemetery.co/google-allo/) before the project was sunset.

## 💭 How it works <a name = "working"></a>

This bot works by using the [IEX API 2.0](https://iexcloud.io/docs/api/). Using various endpoints provided by the API, the bot can take either take commands from users or check any messages for stock symbols as detailed in [Usage](#usage).

## 🎈 Usage <a name = "usage"></a>

### Basic Usage

The simplest way to use the bot is just by sending a message either as a direct message or in a group chat with the bot active. The bot will search every message for text with a dollar sign followed by a stock symbol, and it will return the full name of the company and the current trading price.

```
$tsla
```

The symbols can be anywhere in the message, and you can post as many as you like so commands such as:

```
I wonder if $aapl is down as much as $msft is today.
```

would return the stock price of both Apple and Microsoft like so:

```
The current stock price of Microsoft Corp. is $131.4, the stock is currently up 2.8%

The current stock price of Apple, Inc. is $190.15, the stock is currently up 2.66%
```

### /dividend

To get information about the dividend of a stock type `/dividend` followed by any text that has symbols with a dollar sign in front of them. So, the following command:

```
/dividend $psec
```

Would return information about Prospect Capitals dividend:

```
Prospect Capital Corp. Declares June 2019 Dividend of $0.06 Per Share
The dividend is in: 38 Days 3 Hours 53 Minutes 22 Seconds.
```

💡 you can also call the dividend command using /div

### /news

To get the latest news about a stock symbol use `/news` followed by any text that has symbols with a dollar sign in front of them. So, the following command:

```
/news $psec
```

Would return news for Prospect Capital:

News for PSEC:

[Yield-Starved Investors Still Accumulating BDCs Paying More Than 10% Annually](https://cloud.iexapis.com/v1/news/article/d994b8b5-9fbf-4ceb-afbe-e6defcfc6352)

[Assessing Main Street Capital's Results For Q1 2019 (Includes Updated Price Target And Investment Ratings Analysis)](https://cloud.iexapis.com/v1/news/article/e60899bc-5230-4388-a609-fc2b8736a7d4)

[Fully Assessing Prospect Capital's Fiscal Q3 2019 (Includes Current Recommendation And Price Target)](https://cloud.iexapis.com/v1/news/article/08881160-72c5-4f5d-885b-1751187d24eb)

### /info

To get information about a stock type `/info` followed by any text that has symbols with a dollar sign in front of them. So, the following command:

```
/info $psec
```

Would return information about Prospect Capitals:

Company Name: [Prospect Capital Corp.](http://www.prospectstreet.com/)  
Industry: Investment Managers  
Sector: Finance  
CEO: John Francis Barry  
Description: Prospect Capital Corp. is a business development company, which engages in lending to and investing in private businesses. It also involves in generating current income and long-term capital appreciation through debt and equity investments. The company was founded on April 13, 2004 and is headquartered in New York, NY.

## 🏁 Getting Started <a name = "getting_started"></a>

You can either choose to use the hosted version of the bot by [clicking here](https://t.me/SimpleStockBot) or you can host your own bot with the instructions below.

### Self Hosted Bot

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

This project runs neatly in a docker container, so all that you need to run it yourself is [Docker](https://hub.docker.com/?overlay=onboarding) installed on your system.

You will also need a telegram API key which can be obtained for free by talking to [BotFather](https://telegram.me/botfather), more details [here.](https://core.telegram.org/bots#3-how-do-i-create-a-bot)

Finally, you will need and IEX Cloud API key. They offer a free tier that should be enough for any private groups, more details [here.](https://iexcloud.io/)

### Installing

Once Docker is installed and you have your API keys for Telegram and IEX Cloud getting the bot running on any platform is extremely easy.

Download or clone the repository to your machine and open a terminal in the project and build the Docker container.

```
docker build -t simple-telegram-bot .
```

Then run the bot using your API keys.

```
docker run --detach \
     -e TELEGRAM=TELEGRAM_API \
     -e IEX=IEX_API \
      simple-telegram-bot
```

Your bot should be running! If you are new to Docker, I would recommend checking out its documentation for full control over your bot.

## 🚀 Deploying your own bot <a name = "deployment"></a>

I recommend Digital Ocean for small projects like this because it is straightforward to use and affordable. [Sign up with my referral code, and we both get some free hosting.](https://m.do.co/c/6b5df7ef55b6)

## ⛏️ Built Using <a name = "built_using"></a>

- [python-telegram-bot](https://python-telegram-bot.org/) - Python Telegram API Wrapper
- [Digital Ocean](https://www.digitalocean.com/) - IaaS hosting platform

## ✍️ author <a name = "author"></a>

- [Anson Biggs](https://blog.ansonbiggs.com/author/anson/) - The one and only

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Telegram for having a great bot API
- IEX Cloud for offering a free tier
- Viewers like you ♥

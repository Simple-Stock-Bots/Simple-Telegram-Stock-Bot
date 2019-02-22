# Telegram Bot Commands

## About

If you aren't already, you can talk to this bot here: **[http://t.me/SimpleStockBot](http://t.me/SimpleStockBot)**

Simple Stock Bot is a bot for [Telegram](https://telegram.org/) that provides information about the stock market. You can view the source code [here.](https://gitlab.com/MisterBiggs/simple-telegram-bot). You can also build your own docker container to run [here.](#Build)

_Coded with ❤ by [@MisterBiggs](https://gitlab.com/MisterBiggs)_

## Getting a Stock Quote

Anytime the Bot is in your chat it will search all chats for `$` followed by a ticker. For example `$tsla` will return the following message for Tesla Motors:

```
The current stock price of Tesla Inc. is $321.35, the stock is currently up 2.7%
```

This works no matter where the ticker is in the message and you can have as many tickers as you want in the same message. For example:

```
I wonder how $aapl, $nflx, and $sono are performing today.
```

Will return:

![Conversation With Simple Telegram Bot](img\telegramBotTickerReply.png)

As long as the bot is in your chat it will reply to any stock tickers in your messages.

## Commands

- [`/help`](#/help)
- [`/news`](#/news)
- [`/dividend`](#/dividend)

### /help

This command just displays a short description of what the bot does and a link to this page.

### /news

This command is intelligent enough to get any tickers in the ticker format: `$amzn`, and can handle as many tickers as you would like to enter. The bot will then return the price of the ticker, and links various websites that provide news about the ticker. Currently the command `/news $aapl` returns:

---

`The current stock price of Apple Inc. is $**170.89**, the stock is currently **up 0.86%**`

[`Apple: The 4 Biggest Risks`](https://api.iextrading.com/1.0/stock/aapl/article/7171544094325661)

[`Apple is getting so serious about health, it's started hosting heart-health events at Apple Stores`](https://api.iextrading.com/1.0/stock/aapl/article/6966979968162641)

[`You can now ask Siri to get you directions with Waze so you don't even have to open the app`](https://api.iextrading.com/1.0/stock/aapl/article/7672481171984085)

---

### /dividend

The dividend command will give you the `dividend yield`, `dividend rate`, and will tell you how long until the payout date for any tickers input. Currently the command `/dividend $psec` returns:

---

`Prospect Capital Corporation current dividend yield is: 0.720%, or $11.285 per share.`

`The dividend is in: 14 Days 1 Hours 54 Minutes 46 Seconds.`

---

## Run your own bot using latest build

```powershell
docker run --detach registry.gitlab.com/misterbiggs/simple-telegram-bot:latest
```

## Built and Run your own Bot

You can also run your own bot super easily in a [Docker](https://hub.docker.com/) Container.

1. Download the repository.
2. Change information in [Credentials.py]() with your own Telegram Bot key, which can be found [here.]()
3. Run stockBot.py
4. profit???

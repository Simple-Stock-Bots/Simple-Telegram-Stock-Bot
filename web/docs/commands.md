# Telegram Bot Commands

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

![Conversation With Simple Telegram Bot](\img\telegramBotTickerReply.png)

## Commands

* [`/help`](#/help) - Create a new project.
* [`/news`](#/news) - Start the live-reloading docs server.

### /help

This command just displays a short description of what the bot does and a link to this page.

### /news

This command is intelligent enough to get any tickers in the ticker format: `$amzn`, and can handle as many tickers as you would like to enter. The bot will then return the price of the ticker, and links various websites that provide news about the ticker. Currently for Apple stock the Bot would return:


`The current stock price of Apple Inc. is **$174.18**, the stock is currently up **1.71%**`  
[`Bravos`](https://bravos.co/AAPL)  
[`Seeking Alpha`](https://seekingalpha.com/symbol/AAPL)  
[`MSN Money`](https://www.msn.com/en-us/money/stockdetails?symbol=AAPL)  
[`Yahoo Finance`](https://finance.yahoo.com/quote/AAPL)  
[`Wall Street Journal`](https://quotes.wsj.com/AAPL)  
[`The Street`](https://www.thestreet.com/quote/AAPL.html)  
[`Zacks`](https://www.zacks.com/stock/quote/AAPL)  

*This command needs updating, feel free to [open an issue](https://gitlab.com/MisterBiggs/simple-telegram-bot/issues) with suggestions.*
# Self Hosted Bot

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

## Prerequisites

This project runs neatly in a docker container, so all that you need to run it yourself is [Docker](https://hub.docker.com/?overlay=onboarding) installed on your system.

Depending on what platform you'll need:

- Telegram API key which can be obtained for free by talking to [BotFather](https://telegram.me/botfather), more details [here.](https://core.telegram.org/bots#3-how-do-i-create-a-bot)
- Discord API key which can be obtained for free at [https://discord.com/developers](https://discord.com/developers)

Finally, you will need a [matketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=repo) API key. They offer a free tier that should be enough for any private groups, more details [here.](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=repo)

!!! tip
    The bot will function without a [matketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=repo) key and will fall back to only using cryptocurrency data. 

!!! note
    If you want to accept donations you also need a Stripe API key and provide a `STRIPE` key to your bot. [https://stripe.com/]

## Installing

Once Docker is installed and you have your API keys for Telegram and [matketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=repo) getting the bot running on any platform is extremely easy.

Download or clone the repository to your machine and open a terminal in the project and build the Docker container.

```
docker build -t simple-telegram-bot .
```

Then run the bot using your API keys.

```
docker run --detach \
     -e TELEGRAM=TELEGRAM_API_KEY \
     -e MARKETDATA=MARKETDATA_API_KEY \
      simple-telegram-bot
```

Your bot should be running! If you are new to Docker, I would recommend checking out its documentation for full control over your bot.

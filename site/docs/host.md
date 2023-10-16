# Self-Hosting Guide

This guide provides step-by-step instructions for setting up and running this project on your local machine, whether for development, testing, or personal use.

## Get the Bots

[:fontawesome-brands-telegram: Telegram](https://t.me/SimpleStockBot){ .md-button } [:fontawesome-brands-discord: Discord](https://discordapp.com/api/oauth2/authorize?client_id=532045200823025666&permissions=36507338752&scope=bot){ .md-button }

## Pre-requisites

Ensure the following are installed or obtained before proceeding:

- **[Docker](https://hub.docker.com/?overlay=onboarding)**: The project is containerized using Docker Compose, allowing it to run on any system with Docker installed.
- **API Keys**:
  - **Telegram**: Obtain a free API key by interacting with [BotFather](https://telegram.me/botfather). More details [here](https://core.telegram.org/bots#3-how-do-i-create-a-bot).
  - **Discord**: Get a free API key at [https://discord.com/developers](https://discord.com/developers).
  - **[marketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=web)**: Sign up to get an API key. A free tier is available and should suffice for private groups. More details [here](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=repo).

!!! tip
The bot will still operate without a [marketdata.app](https://dashboard.marketdata.app/marketdata/aff/go/misterbiggs?keyword=repo) key but will revert to using only cryptocurrency data.

!!! note
To enable donation acceptance, obtain a Stripe API key and provide a `STRIPE` key to your bot. [https://stripe.com/]()

## Setup Instructions

1. **Download/Clone the Repository**:

   - Download or clone this repository to your local machine.

2. **Configure Environment Variables**:

   - Navigate to the project directory and locate the `.env` file.
   - Fill in the `.env` file with your obtained API keys:

   ```plaintext
   MARKETDATA=your_marketdata_api_key
   STRIPE=your_stripe_api_key
   TELEGRAM=your_telegram_api_key
   DISCORD=your_discord_api_key
   ```

   Alternatively, pass the variables using Docker Compose environment variables or command-line arguments.

3. **Build and Run the Bot:**

   - Open a terminal in the project directory.
   - Build and run both bots using Docker Compose:

   ```bash
   docker-compose up
   ```

Now, your bot(s) should be up and running! If you're unfamiliar with Docker, reviewing the [Docker documentation](https://docs.docker.com/) is highly recommended to gain better control over your bot and understand Docker commands better.

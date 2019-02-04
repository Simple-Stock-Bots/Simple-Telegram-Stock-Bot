# simple-telegram-bot

## Docker Instructions

Build the Image

```
docker build -t stockbot .
```

Run The image

```
docker run -it --rm --name stockbot stockbot
```

Or run the Image headless

```
docker run -it --rm --detatch --name stockbot stockbot
```
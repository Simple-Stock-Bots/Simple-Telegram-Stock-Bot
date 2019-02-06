# simple-telegram-bot

## Docker Instructions

Build the Image

```powershell
docker build -t stockbot .
```

Run The image

```powershell
docker run -it --rm --name stockbot stockbot
```

Or run the Image headless

```powershell
docker run -it --rm --detatch --name stockbot stockbot
```
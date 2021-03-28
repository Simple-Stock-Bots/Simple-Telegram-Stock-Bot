FROM python:3.9-buster



COPY requirements.txt ./
RUN pip install --no-cache-dir -U -r requirements.txt

COPY . .

CMD [ "python", "./bot.py" ]
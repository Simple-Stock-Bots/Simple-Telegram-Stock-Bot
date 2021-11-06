FROM python:3.9-buster AS builder


COPY requirements.txt /requirements.txt
RUN pip install --user -r requirements.txt


FROM python:3.9-slim

COPY --from=builder /root/.local /root/.local


COPY . .

CMD [ "python", "./bot.py" ]
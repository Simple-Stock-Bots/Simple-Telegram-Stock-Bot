FROM python:3.11-buster AS builder


COPY telegram/telegram-reqs.txt .
COPY common/requirements.txt .

RUN pip install --user -r telegram-reqs.txt


FROM python:3.11-slim

ENV MPLBACKEND=Agg

COPY --from=builder /root/.local /root/.local


COPY common common
COPY telegram .



CMD [ "python", "./bot.py" ]
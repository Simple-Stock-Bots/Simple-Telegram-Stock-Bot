FROM python:3.11-buster AS builder


COPY discord/requirements.txt .

RUN pip install --user -r requirements.txt


FROM python:3.11-slim

ENV MPLBACKEND=Agg

COPY --from=builder /root/.local /root/.local

COPY common common
COPY discord .

CMD [ "python", "./bot.py" ]
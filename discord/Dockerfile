FROM python:3.11-buster AS builder


COPY discord/discord-reqs.txt .
COPY common/requirements.txt .

RUN pip install --user -r discord-reqs.txt


FROM python:3.11-slim

ENV MPLBACKEND=Agg

COPY --from=builder /root/.local /root/.local

COPY common common
COPY discord .

CMD [ "python", "./bot.py" ]
FROM python:3.11-slim

WORKDIR /app
RUN mkdir /config
COPY . .

RUN apt update
RUN apt install build-essential libssl-dev libffi-dev rustc -y
RUN apt install libpq-dev python-dev python3-dev -y

RUN pip install -U pip
RUN pip3 install -r requirements.txt

CMD [ "/bin/bash", "-c", "cp /conf/.env .env; alembic upgrade head; python3 main.py" ]

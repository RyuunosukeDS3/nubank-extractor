FROM python:3
WORKDIR /app
RUN mkdir /workspace
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN touch .env
RUN echo "CPF=\nPASSWORD=\nCERT_PATH=/workspace/cert.p12\nDB_URI=\nRUN_TIME=20:00" >> .env

COPY . .

CMD [ "/bin/bash", "-c", "cp -a /app/. /workspace/ ;cd /workspace; alembic upgrade head; python3 main.py" ]
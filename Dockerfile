FROM python:3.11-alpine

WORKDIR /app

ENV NAMESPACE = cjarcau
ENV OLDER_THEN = 20
ENV POSTGRES_USER = postgres
ENV POSTGRES_PASSWORD = password
ENV POSTGRES_HOST = 127.0.0.1
ENV POSTGRES_PORT = 5432
ENV POSTGRES_DB = postgres

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]

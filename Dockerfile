FROM python:3.11-alpine

WORKDIR /app

ENV NAMESPACE = cjarcau
ENV OLDER_THEN = 10

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]

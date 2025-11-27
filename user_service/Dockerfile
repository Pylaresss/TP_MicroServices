FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY . /app

ENV PYTHONUNBUFFERED=1

EXPOSE 5002

CMD ["python", "run.py"]

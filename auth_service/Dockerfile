FROM python:3.11-slim

WORKDIR /app

# flask + requests + authlib pour les JWT
RUN pip install --no-cache-dir flask requests authlib

COPY . /app

ENV PYTHONUNBUFFERED=1

EXPOSE 5001

CMD ["python", "run.py"]

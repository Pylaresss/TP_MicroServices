FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
RUN pip install --no-cache-dir flask requests

# Copier le code
COPY . /app

# Pour avoir les logs en direct
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "run.py"]

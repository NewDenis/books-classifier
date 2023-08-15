FROM python:3.9.13-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH       "${PYTHONPATH}:/app:/base:/app/books_classifier"
ENV PATH             "${PATH}:/app"

COPY ./requirements.txt /app/requirements.txt

RUN apt update && apt install wget locales gcc build-essential nano htop curl python3.9-dev libomp-dev s3cmd -y && apt-get clean
# RUN chmod o+rw -R /usr/local/lib/python3.9/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app
# CMD ["uvicorn", "books_classifier.app.main:app_factory", "--factory", "--host", "0.0.0.0", "--port", "80"]
# COPY ./books_classifier/artifacts/models /app/books_classifier/artifacts/models
COPY . /app
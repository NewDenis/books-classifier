FROM apache/airflow:slim-2.7.0rc1-python3.9

# ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH       "${PYTHONPATH}:/app:/base"
ENV PATH             "${PATH}:/app"

COPY . /app

USER root
RUN apt update && apt install wget locales gcc build-essential nano htop curl python3.9-dev libomp-dev -y && apt-get clean
# RUN chmod o+rw -R /usr/local/lib/python3.9/
USER airflow
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# CMD ["uvicorn", "books_classifier.app.main:app_factory", "--factory", "--host", "0.0.0.0", "--port", "80"]

FROM python:3.9.13-slim
ARG PYPI_TOKEN

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH       "${PYTHONPATH}:/app:/base"
ENV PATH             "${PATH}:/app"

WORKDIR /app
COPY . /app

RUN apt update && apt install wget locales gcc build-essential nano htop curl python3.9-dev libomp-dev -y && apt-get clean
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

RUN sed -i -e \
  's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
   && locale-gen
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
ENV TZ Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD ["uvicorn", "app.main:app_factory", "--factory", "--host", "0.0.0.0", "--port", "80"]

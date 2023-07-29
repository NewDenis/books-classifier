PYTHON_VERSION = 3.9.13
VENV_NAME = books_classifier
DVC_MODEL_ARTIFACTORY = books_storage
DOCKER_CONTAINER_LOCAL_NAME = books_classifier


venv:
	@echo "Создание виртуального окружения"
	pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME); \
	pyenv shell $(VENV_NAME); \
	pyenv local $(VENV_NAME)


check-python-version:
	@echo "Проверка версии питона"
	pyenv which python; \
	pyenv which pip


install-poetry:
	@echo "Установка poetry + запрет для poetry создавать внутри виртуальное окружение"
	pip install --upgrade pip poetry; \
	poetry config virtualenvs.create false


dep-install:
	@echo "Установка зависимостей из poetry.lock"
	poetry install


gen-dvc:
	@echo "Генерация DVC конфига"
	envsubst < ./.dvc/config.templ > ./.dvc/config


reformat:
	@echo "Переформатирование файлов с кодов, если есть необходимость"
	isort .
	black --line-length 79 .

load-models:
	@echo "Загрузить модели из S3"
	dvc pull -r $(DVC_MODEL_ARTIFACTORY) <USED_MODEL_1>

build:
	@echo "Сборка контейнера $(DOCKER_CONTAINER_LOCAL_NAME)"
	docker build -t $(DOCKER_CONTAINER_LOCAL_NAME) .

up:
	@echo "Подъем контейнера $(DOCKER_CONTAINER_LOCAL_NAME)"
	docker-compose -f docker-compose.local.yml up

docker-connect:
	@echo "Присоединиться к контейнеру $(DOCKER_CONTAINER_LOCAL_NAME) (локально)"
	docker exec -it $(DOCKER_CONTAINER_LOCAL_NAME) sh

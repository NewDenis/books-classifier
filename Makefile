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

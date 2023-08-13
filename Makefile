PYTHON_VERSION = 3.9.13
VENV_NAME = books_classifier
DVC_MODEL_ARTIFACTORY = books_storage
DOCKER_CONTAINER_LOCAL_NAME = books_classifier


gen-dvc:
	@echo "Генерация DVC конфига"
	envsubst < ./.dvc/config.templ > ./.dvc/config

gen-req:
	@echo "Генерация requirements.txt из poetry"
	echo "poetry-core>=1.6.1" | tee requirements.txt
	poetry export --without-hashes | grep -v "@ file" >> requirements.txt
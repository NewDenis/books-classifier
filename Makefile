PYTHON_VERSION = 3.9.13
VENV_NAME = books_classifier
DVC_MODEL_ARTIFACTORY = books_storage
DOCKER_CONTAINER_LOCAL_NAME = books-classifier
DOCKER_VERSION = 0.2.5


gen-dvc:
	@echo "Генерация DVC конфига"
	envsubst < ./.dvc/config.templ > ./.dvc/config

gen-req:
	@echo "Генерация requirements.txt из poetry"
	echo "poetry-core>=1.6.1" | tee requirements.txt
	poetry export --without-hashes | grep -v "@ file" | grep -v extract-msg >> requirements.txt

build:
	@echo "Build docker image"
	docker build . -t pimenovdv/${DOCKER_CONTAINER_LOCAL_NAME}:${DOCKER_VERSION}

push:
	@echo "Push docker image"
	docker push pimenovdv/${DOCKER_CONTAINER_LOCAL_NAME}:${DOCKER_VERSION}
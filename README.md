# books_classifier

Разработка предполагается исключительно на `Linux`

<span style="color:red">После генерация необходимо обратить внимание на Dockerfile, 
в нем установлена `python3.9-dev`, которая актуальна только для 
`python 3.9`, если в указанном образе другой питон, то его нужно заменить!</span>


Как развернуть приложение?

1. Install `pyenv`
```bash
curl https://pyenv.run | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

exec "$SHELL"
```


2. Установка необходимой версии python 3.9.13
```bash
pyenv install 3.9.13
```

3. Создание окружения
Для единообразия и простоты предлагается называть окружение в pyenv,
так же как и сам сервис
```bash
make venv
```

4. Активация созданного окружения make не хочет обновлять консоль, 
поэтому активацию приходится делать отдельной командой
```bash
pyenv activate 
```

5. Проверка версии питона
```bash
make check-python-version
```

6. Установка poetry (установка всех зависимостей будет происходить через poetry, чтобы было меньше проблем с зависимостями)
Так же запрещаем poetry создавать окружение внутри проекта
Иначе `poetry` будет постоянно намереваться создавать окружение внутри проекта
```bash
make install-poetry
```

7. Установка зависимостей из poetry.lock
```bash
make dep-install
```

8. Генерация настроек DVC
Если в проекте не предполагается использовать dvc, то
можно удалить `.dvc/`
Для генерации конфига, необходимо, чтобы в .bashrc были установлены 
переменные окружения
```
export ACCESS_KEY_ID=<key>
export SECRET_ACCESS_ID=<key>
```
```bash
make gen-dvc 
```


9. Выбрать новосозданный интерпретатор питона из окружения books_classifier для работы с проектом

10. Создание `pre-commit` хука
Важно чтобы проект уже версионировался git'ом
```bash
echo "make reformat" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

11. Установка Airflow в Kubernetes с GitSync

Создаём ключ SSH для репозитория
```bash
ssh-keygen -t rsa -b 4096 -C "<email>"
```
> Важно! Лучше использовать нестандартное название файла

Публичный ключ (.pub) нужно добавить в репозиторий гита
```bash
export SECRET_GIT_SSH_KEY=$(base64 <имя файла приватного ключа> -w 0)
envsubst < ./k8s/override-values-template.yaml > ./k8s/override-values.yaml
helm upgrade --install airflow apache-airflow/airflow -f ./k8s/override-values.yaml
```

12. Kubernetes Secrets Setting
```
kubectl create secret generic dvc-config --from-file config=./.dvc/config
kubectl create secret generic aws-credentials --from-file credentials=~/.aws/credentials
```



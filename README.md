# Foodgram

## Фудграм - это сайт-блог для пользователей, который позволяет создавать свои рецепты, делиться ими с другими, скачивать рецепты и подписываться на других авторов. 

## Блог включает в себя:

- Систему постов-рецептов.
- Базу ингредиентов, реализованных через отдельную модель.
- Модель тегов.
- Подписки пользователей на авторов.
- Добавление рецептов в избранное. 
- Скачивание списка ингредиентов в txt-файл.

## Необходимые знания

Для работы с данным проектом вам понадобятся следующие знания и навыки:

[![Python](https://img.shields.io/badge/-Python_3.9.10-464646??style=flat-square&logo=Python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/-Django-464646??style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django](https://img.shields.io/badge/-Django_rest_framework_3.12.4-464646??style=flat-square&logo=Django)](https://www.django-rest-framework.org)
[![Docker](https://img.shields.io/badge/-Docker-464646??style=flat-square&logo=Docker)](https://hub.docker.com/)
[![Nginx](https://img.shields.io/badge/-Nginx-464646??style=flat-square&logo=Nginx)](https://nginx.org/ru/)
[![Gunicorn](https://img.shields.io/badge/-gunicorn-464646??style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![CI/CD](https://img.shields.io/badge/-CI/CD-464646??style=flat-square&logo=CI/CD)](https://resources.github.com/ci-cd/)
[![GitHab](https://img.shields.io/badge/-GitHab-464646??style=flat-square&logo=GitHab)](https://github.com)


# Локальная установка и запуск приложения Фудграм

1. В терминале создайте папку проекта, перейдите в нее для клонирования репозитория.

```sh
git clone https://github.com/ArtemSelivanov33/foodgram.git
```

2. Разверните виртуальное окружение

Windows:
```sh
python -m venv venv
```
Linux, MacOS:
```sh
python3 -m venv venv
```
Далее в инструкции будем использовать команду "python".

3. в директории с папкой venv активируйте виртуальное окружение

Windows:
```sh
source venv\Scripts\activate
```
Linux, MacOS:
```sh
source venv\bin\activate
```
4. Перейдите в папку с файлом requirements.txt и установите зависимости
```sh
pip install -r requirements.txt
```
5. В той же папке введите команды применения миграций проекта.
```sh
python manage.py makemigrations
python manage.py migrate
```
6. После применения миграций можно ввести команду создания суперпользователя и следовать указаниям терминала
```sh
python manage.py createsuperuser
```
7. Запуск локального сервера

```sh
python manage.py runserver
```

8. В адресной строке браузера наберите адрес API или админки и проверьте работу сайта

```sh
http://127.0.0.1:8000/api/
http://127.0.0.1:8000/admin/
```

# Разворачивание проекта в Docker на удаленном сервере

Деплой проекта на сервер происходит по этапам, описанным в файле .github\workflows\main.yml. Перед первым деплоем проекта необходимо в Secrets репозитория указать значения некоторых констант.


- Константы для Secrets проекта
```sh
DOCKER_USERNAME                # имя пользователя в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub
HOST                           # ip_address сервера
USER                           # имя пользователя на сервере
SSH_KEY                        # приватный ssh-ключ
SSH_PASSPHRASE                 # кодовая фраза (пароль) для ssh-ключа
SECRET_KEY                     # секретный ключ вашего проекта
ALLOWED_HOSTS                  # список хостов вашего проекта

TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
DB_HOST                        # foodgram-db-1(название базы данных.по-умолчанию, название контейнера где запущена база данных)
DB_NAME                        # db
DB_PORT                        # 5432
DEBUG                          # False
POSTGRES_DB                    # db
POSTGRES_PASSWORD              # foodgram_password
POSTGRES_USER                  # foodgram_user
```


Инструкция main.yml предусматривает деплой проекта после каждого пуша изменений в репозиторий на гит. Первичный деплой проекта тоже происходит после этой команды

```sh
git push
```

> Первичное разворачивание контейнеров на сервере производится по инструкции в файле docker-compose.yml. 
> Далее каждый деплой изменений в проекте происходит по инструкции docker-compose.production.yml.
> Оба файла копируются на сервер автоматически после срабатывания скрипта из main.yml. 
> Файл .env с переменными окружения формируется по инструкции из main.yml, значения переменных берутся в Secrets.


# Установка проекта на сервер вручную

1. Клонируйте репозиторий на свой компьютер:

    ```sh
    git clone https://github.com/ArtemSelivanov33/foodgram.git
    ```
    ```sh
    cd foodgram
    ```
2. Создайте файл .env и заполните его своими данными. Перечень данных указан в корневой директории проекта в файле .env.example.


## Создание Docker-образов

1.  Замените username на ваш логин на DockerHub:

    ```sh
    cd frontend
    docker build -t username/foodgram_frontend .
    cd ../backend
    docker build -t username/foodgram_backend .
    cd ../nginx
    docker build -t username/foodgram_gateway . 
    ```

2. Загрузите образы на DockerHub:

    ```sh
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    docker push username/foodgram_gateway
    ```

## Деплой на сервере

1. Подключитесь к удаленному серверу

    ```sh
    ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
    ```

2. Создайте на сервере директорию foodgram через терминал

    ```sh
    mkdir foodgram
    ```

3. Установка docker compose на сервер:

    ```sh
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin
    ```

4. В директорию foodgram/ скопируйте файлы docker-compose.production.yml и .env:

    ```sh
    scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
    * path_to_SSH — путь к файлу с SSH-ключом;
    * SSH_name — имя файла с SSH-ключом (без расширения);
    * username — ваше имя пользователя на сервере;
    * server_ip — IP вашего сервера.
    ```

5. Запустите docker compose в режиме демона:

    ```sh
    sudo docker compose -f docker-compose.production.yml up -d
    ```

6. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:

    ```sh
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
    ```


# Команды которые могут пригодиться в процессе

1. 
    ```sh
    sudo docker compose -f docker-compose.production.yml ps  # проверка контейнеров
    ``` 
    ```sh
    sudo docker compose -f docker-compose.production.yml .. (stop, pull, down, logs)  # команды для контейнеров
    ```
    ```sh
    git add .
    git commit -m 'Add Actions'  # пуш на Гитхаб
    git push
    ```
    ```sh
    sudo docker exec -it foodgram-db-1  psql -U foodgram_user -d db  # подключение к базе PostgreSQL,используя консольный клиент psql.
    ```
    ```sh
    \help  \l  \dt  # команда psql
    ```
    ```sh
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients  # команда на сервере для загрузки ингредиентов в базу данных,
                                                                                                           # выполняется в отдельном окне терминала.
    ```
    ```sh
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser  # создание суперпользователя
    ```

## Автор: Селиванов Артем, студент 96 когорты.

```
http://51.250.83.28
admin@mail.ru
0127923
```

## Описание проекта Foodgram

Foodgram - сайт для публикации ваших рецептов.Здесь вы можете оставлять 
свои рецепты, смотреть другие и даже формировать список покупок!
## Что нужно сделать чтобы протестировать у себя локально?

* Склонируйте к себе репозиторий по команде:
```
git clone https://github.com/salbadys/foodgram-project-react.git
```

* Cоздайте и активируйте виртуальное окружение(только если у вас не PyCharm):

```
python -m venv venv
```

```
source venv/Scripts/activate
```

* Cоздайте файл `.env` в директории `/infra/` с содержанием:

```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=0127923a # пароль для подключения к БД (установите свой)
DB_HOST=db # название  сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

* Установите пакеты с requirements.txt:

```
cd backend
pip install -r requirements.txt
```

* Выполните миграции:

```
python manage.py makemigrations
python manage.py migrate
```

* Запустите сервер:
```
python manage.py runserver
```

* Стучись на адрес:
```
127.0.0.1:8000
```

## Запуск проекта в Docker
* Установите Docker.
```
https://www.docker.com
```

Файлы для сборки и параметры находятся в папке infra/ -  docker-compose.
yml и nginx.

* Запустите сборку - docker compose:
```
docker-compose up -d --build
```  
  > После сборки появляются 4 контейнера:
  > 1. контейнер db
  > 2. контейнер backend
  > 3. контейнер nginx
  ```
4-ый контейнер frontend не используется, но будет в списке.
```  
* Выполните миграции:
```
docker-compose exec backend python manage.py migrate
```
* Создайте администратора:
```
docker-compose exec backend python manage.py createsuperuser
```
* Соберите статику:
```
docker-compose exec backend python manage.py collectstatic --noinput
```
```
Стучаться можно на localhost
```


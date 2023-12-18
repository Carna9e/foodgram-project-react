# Foodgram - Учебный проект Яндекс.Практикум
#  Как работать с репозиторием финального задания

## Описание проекта

Данный проект создан в процессе обучения на платформе Яндекс Практикум. Зарегистрированные пользователи могут публиковать свои рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в «Избранное», а также в «Список покупок», из которого формируется доступный для скачивания список продуктов, необходимых для приготовления всех блюд, добавленных в «Список покупок».

## Технологии

1. Django==3.2.3
2. Djangorestframework==3.12.4
3. Python==3.9
4. Nginx==1.22.1
5. Gunicorn==20.1.0
6. Docker
7. PostgreSQL

## Как запустить проект:

- Установить программу контейнеризации Docker (версия 4.24.2), так же необходимо зарегистрироваться на DockerHub.

- Клонировать репозиторий: `git clone <адрес вашего репозитория>`

- Создаем файл `.env` по образцу `.env.example`

- В терминале выполнить запуск: 

  `sudo docker compose -f docker-compose.production.yml up`

- Выполняем сбор статистики и применяем миграции бэкенда:

```
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
  sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

- Создать суперпользователя:

  `sudo docker compose -f docker-compose.production.yml exec backend python manage.py creatsuperuser`

## Для локального запуска 

- Создайте и активируйте виртуальное окружение:
```
  python3 -m venv env
  source venv/Scripts/activate
```
- Установите в него зависимости из `backend/requirements.txt`, выполните миграции, сбор статики, создайте суперпользователя.

## Автор
- Евгений Зуев


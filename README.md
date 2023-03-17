# Учебный проект "Foodgram-project-react"

«Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

### Авторы:
- Daniil Bibikov (Jon-Makkonahi) https://github.com/Jon-Makkonahi

![130495494-1eb4c107-209a-40cd-a4ac-12f40762725b](https://user-images.githubusercontent.com/88703195/225973965-95cc773b-56d7-4166-9310-eed519880619.jpg)


### Технологии:
- Python
- Django
- DRF
- SQLite3
- PostgeSQL

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Jon-Makkonahi/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt (до этого вынести файл requirements.txt из папки backend)
```

Выполнить миграции:
перейдите в backend папку проекта, где находится  manage.py
```
python3 manage.py migrate
```

Если необходимо, заполненить базу данных тестовыми данными:

1. перейдите в backend папку проекта, где находится manage.py
2. запустите скрипт loadjson.py:
```
python manage.py loadjson --path 'recipes/data/ingredients.json'
```

## Запуск Docker:
Запустите docker-compose командой 

```bash
sudo docker-compose up -d --build
```
У вас развернётся проект, запущенный через Gunicorn с базой данных Postgres.
Выполнить миграции, создать суперпользователя и заполнить БД данными, а также собрать статику.

```bash
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py loadjson --path 'recipes/data/ingredients.json'
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
Остановка контейнеров и их удаление вместе со всеми зависимостями
```bash
sudo docker-compose down -v
```
Ссылка на проект
```
http://51.250.86.0/
```

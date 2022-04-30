# Учебный проект "Foodgram-project-react"

«Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

### Авторы:
- Daniil Bibikov (Jon-Makkonahi) https://github.com/Jon-Makkonahi

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
перейдите в backend папку проекта, где находится папка с manage.py
```
python3 manage.py migrate
```

Если необходимо, заполненить базу данных тестовыми данными:

1. перейдите в backend папку проекта, где находится папка с manage.py
2. запустите скрипт loadjson.py:
```
python manage.py loadjson --path 'recipes/data/ingredients.json'
```

Регистрация нового пользователя:

```
http://51.250.86.0/signup
```
## Для ревьера:
http://51.250.86.0/ - сайт

http://51.250.86.0/admin - админка

login JonMakko
password eTuzHX3f

# Yatube
### Описание
Социальная сеть для блогеров.

* Создавайте и редактируйте свои посты.
* Подписывайте на любимых авторов.
* Делитесь своим мнением в комментариях к постам.

![demo-gif](https://github.com/ArslanYadov/hw05_final/blob/master/presentation/yatube_presentation.gif)
### Технологии
* [Python 3.7](https://docs.python.org/3.7/)
* [Django 2.2.19](https://docs.djangoproject.com/en/4.1/)
## Запуск проекта в dev-режиме
- В корневой директории проекта создать файл ```.env``` и установить свои значения для ```SECRET_KEY```, ```DEBUG``` и ```POSTS_AMOUNT_PER_PAGE```
```
SECRET_KEY = 'Your_secret_key'
DEBUG = True # for dev-mode
POSTS_AMOUNT_PER_PAGE = 10 # Your amount posts for page
```
- Установить виртуальное окружение
```
$ python -m venv venv
```
- Активировать виртуальное окружение
```
$ source venv/Scripts/activate
```
- Установить зависимости из файла requirements.txt
```
$ pip install -r requirements.txt
```
- В папке с файлом manage.py выполнить миграции:
```
$ python manage.py migrate
```
- Запустить dev-сервер:
```
$ python manage.py runserver
```
## Автор
Арслан Ядов

E-mail: [Arslan Yadov](mailto:arsyy90@gmail.com?subject=%20Yatube%20project)

# RegistryGift-Backend
Proyecto de taller V

## Instalación:
En una terminal en la carpeta raíz:
1. `python -m venv venv`
2. `venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python manage.py makemigrations`
5. `python manage.py migrate`
6. `python manage.py runserver`

## Unit Tests:
En una terminal en la carpeta raiz:
1. `venv\Scripts\activate`
2. `python manage.py test registry`

## Unit Test Coverage:
En una terminal en la carpeta raiz:
1. `venv\Scripts\activate`
2. `coverage run manage.py test registry`
3. `coverage report` o `coverage html`
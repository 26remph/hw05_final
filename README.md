<div>
    <h1>
        <img hspace="6px" align="center" src="./yatube/static/img/logo.png" width="60"/>
        <span>$\textcolor{red}{\text{Ya}}{\text{tube}}$</span>
    </h1>
</div>
<br>
<br>

# Социальная сеть для публикации блогов

## Описание:  
Социальная сеть блогеров. Она даст пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и комментировать понравившиеся записи.

Технологии:
* Python 3.8
* Django framework 2.2.16
* HTML+CSS (Bootstrap 3)
* jwt token authorize
* Pillow 8.3.1
* sorl-thumbnail 12.7.0
* unittest (Unit test framework)

### Покрытие тестами
Покрытие тестами выполнено при помощи unittest(Unit test framework)
Тесты находятся в папке `./yatube/posts/test/`. Модуль теста начинается со слова `test_`. Тесты покрывают следующие области:

- тесты кэширования страниц 
- тесты комментариев
- тесты следования и подписок на авторов
- тесты форм
- тесты загрузки изображений
- тесты моделей базы данных
- тесты URL проекта
- тесты view функций

Каждому тесту соответствует отдельный файл.

## Запуск проекта в dev-режиме:

Клонируйте репозиторий и перейти в него в командной строке: 

    git clone https://github.com/26Remph/hw05_final.git

Установите и активируйте виртуальное окружение: 

    python -m venv env source env/bin/activate

Установите зависимости из файла requirements.txt:   
    
    pip install -r requirements.txt

Выполните миграции: 

    python manage.py migrate

В папке с файлом manage.py выполните команду:  

    python manage.py runserver

## Запуск unittest тестов:
Тесты запускаются из папки в которой находятся. Флаг -v показывает более детальный отчет. 
    
    python3 -m unittest -v test_<имя_модуля_теста>.py
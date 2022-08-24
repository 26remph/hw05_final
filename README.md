<div>
    <h1>
        <img hspace="6px" align="center" src="./yatube/static/img/logo.png" width="60"/>
        <span>$\textcolor{red}{\text{Ya}}{\text{tube}}
            123$</span>
    </h1>
    <h5>
        (социальная сеть для публикации блогов)
    </h5>
</div>
<br>
<br>
<br>


## Описание:  
Социальная сеть блогеров. Она даст пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и комментировать понравившиеся записи.

Технологии:
* Python 3.8
* Django framework 2.2.16
* HTML+CSS (Bootstrap 3)
* jwt token authorize
* Pillow 8.3.1
* sorl-thumbnail 12.7.0

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

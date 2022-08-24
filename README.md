<div>
    <h1>
        <img hspace="6px" align="center" src="./yatube/static/img/logo.png" width="60"/>
        <span style="color:red">- Ya -</span><span>tube</span>
    </h1>
</div>

-ya-
-YA-

<svg viewBox="0 0 240 80" xmlns="http://www.w3.org/2000/svg">
  <style>
    .small { font: italic 13px sans-serif; }
    .heavy { font: bold 30px sans-serif; }

    /* Note that the color of the text is set with the    *
     * fill property, the color property is for HTML only */
    .Rrrrr { font: italic 40px serif; fill: red; }
  </style>

  <text x="20" y="35" class="small">My</text>
  <text x="40" y="35" class="heavy">cat</text>
  <text x="55" y="55" class="small">is</text>
  <text x="65" y="55" class="Rrrrr">Grumpy!</text>
</svg>


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

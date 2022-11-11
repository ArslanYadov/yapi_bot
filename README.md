# yAPI_Bot
## Описание
Телеграм бот автоматизирует проверку статуса ревью по проектам Яндекс.Практикума.
## Технологии
- [Python 3.7.0](https://docs.python.org/3.7/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
## Запуск телеграм бота
- В корневой директории проекта создать файл `.env` и наполнить его по примеру из файла `.env.template`
``` python
PRACTICUM_TOKEN = 'your_token_from_yandex_practikum_api'
TELEGRAM_TOKEN = 'tg_token_from_bot_father'
TELEGRAM_CHAT_ID = 'tg_chat_id'
```
- Установить и активировать виртуальное окружение
``` bash
$ python3 -m venv venv; . venv/bin/activate
```
- Установить зависимости
``` bash
$ python -m pip install -U pip; pip install -r requirements.txt
```
- Перейти в каталог `./yapi_bot` и запустить бота
``` bash
$ cd yapi_bot; python status_check.py
```
## Автор
Арслан Ядов

E-mail: [Arslan Yadov](mailto:arsyy90@gmail.com?subject=Telegram%20Bot%20YP)
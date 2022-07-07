import os
import time
import telegram
import requests
import logging
import sys

from http import HTTPStatus
from dotenv import load_dotenv


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 10 * 60
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('main.log'),
        logging.StreamHandler(sys.stdout)
    ]
)


def send_message(bot, message):
    """Отправка сообщения ботом."""
    return bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """Запрок к API Яндекса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        error = (
            f'Эндпоинт {ENDPOINT} недоступен. '
            f'Код ответа API: {response.status_code}'
        )
        logging.error(error)
        raise ConnectionError(error)

    response = response.json()
    return response


def check_response(response):
    """Проверка ответа от API."""
    try:
        response_list = response['homeworks']
        if type(response_list) is not list:
            error = 'Получен словарь, вместо списка'
            logging.error(error)
            raise TypeError(error)
    except KeyError:
        error = 'Отсутствие ожидаемых ключей в ответе API.'
        logging.error(error)
        raise KeyError(error)
    except IndexError:
        error = 'Ответ от API содержит пустой словарь.'
        logging.error(error)
        raise IndexError(error)
    return response_list


def parse_status(homework):
    """Получение названия домашней работы и ее статуса."""
    homework_name = homework['homework_name']

    homework_status = homework.get('status')
    if homework_status is None:
        error = 'Не получен статус домашней работы.'
        logging.error(error)
        raise KeyError(error)

    verdict = ''
    for status, message in HOMEWORK_STATUSES.items():
        if homework_status == status:
            verdict += message
    if verdict == '':
        error = 'Недокументированный статус домашней работы.'
        logging.error(error)
        raise Exception(error)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка токенов."""
    tokens = (
        (PRACTICUM_TOKEN, 'PRACTICUM_TOKEN'),
        (TELEGRAM_TOKEN, 'TELEGRAM_TOKEN'),
        (TELEGRAM_CHAT_ID, 'TELEGRAM_CHAT_ID'),
    )
    for token, token_name in tokens:
        if token is None:
            logging.critical(
                f'Отсутствует обязательная переменная окружения: {token_name}'
                '\nПрограмма принудительно остановленна.'
            )
            return False
        return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise ValueError('Token error')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = check_response(get_api_answer(current_timestamp))
            if len(response) > 0:
                homework = response[0]
                message = parse_status(homework)
                send_message(bot, message)
                logging.info(f'Бот отправил сообщение: "{message}"')
            else:
                message = 'Нет работ отправленных на проверку.'
                send_message(bot, message)
                logging.info(f'Бот отправил сообщение: "{message}"')

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logging.info(f'Бот отправил сообщение: "{message}"')
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

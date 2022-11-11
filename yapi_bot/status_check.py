import os
import time
import telegram
import requests
import logging
import sys

from exceptions import BotSendMessageError
from http import HTTPStatus
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = int(10 * 60)
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения ботом."""
    logging.info(f'Начата отправка сообщения: "{message}"')
    try:
        return bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.BadRequest:
        raise BotSendMessageError(
            'Вознокла ошибка при отправке сообщения ботом.'
        )


def get_api_answer(current_timestamp):
    """Запрос к API Яндекса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        logging.info('Делаем GET запрос к эндпоинту API Яндекса')
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            error = (
                f'Эндпоинт {ENDPOINT} недоступен. '
                f'Код ответа API: {response.status_code}'
            )
            raise ConnectionError(error)
    except ConnectionError:
        raise ConnectionError(error)

    return response.json()


def check_response(response):
    """Проверка ответа от API."""
    logging.info('Начата проверка ответа от API.')

    if len(response) == 0:
        raise IndexError('Ответ от API содержит пустой словарь.')

    if not isinstance(response, dict):
        raise TypeError('Ответ не является словарем.')

    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError('Отсутствие ожидаемых ключей в ответе API.')

    homework_list = response['homeworks']
    if not isinstance(homework_list, list):
        raise TypeError('Ответ не является списком.')

    return homework_list


def parse_status(homework):
    """Получение названия домашней работы и ее статуса."""
    logging.info('Начата проверка названия домашней работы.')
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise KeyError('Не полученно имя домашней работы.')

    logging.info('Начата проверка статуса домашней работы.')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError('Не получен статус домашней работы.')

    verdict = HOMEWORK_VERDICTS[homework_status]
    if verdict is None:
        raise Exception('Недокументированный статус домашней работы.')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка токенов."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    logging.info('Начата проверка токенов')
    if not check_tokens():
        message = (
            'Отсутствует обязательная переменная окружения'
            '\nПрограмма принудительно остановленна.'
        )
        logging.critical(message)
        sys.exit(message)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    old_message = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            current_timestamp = response.get('current_date')

            if len(homework) > 0:
                message = parse_status(homework[0])
                if message != old_message:
                    send_message(bot, message)
                    logging.info(f'Бот отправил сообщение: "{message}"')
                old_message = message
        except Exception as error:
            logging.error(error)
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logging.info(f'Бот отправил сообщение: "{message}"')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s, [%(levelname)s] - %(message)s',
        handlers=[
            logging.FileHandler('main.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    main()

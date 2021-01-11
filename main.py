import requests
from requests.exceptions import ReadTimeout, HTTPError
import os
import telegram
import time
import logging


bot_logger = logging.getLogger("bot_logger")
DEVMAN_API='https://dvmn.org/api/'

class BotLogsHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)
        self.bot =  telegram.Bot(token=os.environ['TELEGRAMM_LOGGER_BOT'])
        self.chat_id = os.environ["TELEGRAM_CHAT_ID"]

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)

if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s %(message)s")
    bot_logger.setLevel(logging.INFO)
    bot_logger.addHandler(BotLogsHandler())

    header = {'Authorization': f'Token {os.environ["DEVMAN_TOKEN"]}'}
    bot = telegram.Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    timestamp = None
    bot_logger.info('Бот запущен!')

    while True:
        try:
            request_param = {'timestamp': timestamp}
            response = requests.get(f'{DEVMAN_API}long_polling/', params=request_param, headers=header, timeout=95)
            response.raise_for_status()
            response_data = response.json()
            status = response_data['status']
            if status == 'timeout':
                timestamp = response_data['timestamp_to_request']
            else:
                timestamp = response_data['last_attempt_timestamp']
                for attempts in response_data['new_attempts']:
                    work_status = attempts['is_negative']
                    title = attempts['lesson_title']
                    url = f"https://dvmn.org{attempts['lesson_url']}"
                    if work_status:
                        message_text = f'''У вас проверили работу «{title}»
                                       \nК сожалению нашлись ошибки.
                                       \nСсылка на урок: {url}'''
                    else:
                        message_text = f'''У вас проверили работу «{title}»
                                       \nПреподавателю все понравилось, можно приступать к следующему уроку!
                                       \nСсылка на урок: {url}'''

                    bot.send_message(chat_id=chat_id, text=message_text)
        except ReadTimeout:
            pass
        except ConnectionError as error:
            bot_logger.error(f'В работе бота возникла ошибка:\n{error}',exc_info=True)
            time.sleep(60)
        except HTTPError as error:
            bot_logger.error(f'В работе бота возникла ошибка:\n{error}',exc_info=True)
            bot.send_message(chat_id=chat_id, text='Ошибка сервера!\nСервер времено не доступен!')
            time.sleep(60)
        except Exception as error:
            bot_logger.error(f'В работе бота возникла ошибка:\n{error}',exc_info=True)
            time.sleep(60)
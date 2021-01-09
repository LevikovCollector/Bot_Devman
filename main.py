import requests
from requests.exceptions import ReadTimeout, HTTPError
import os
from dotenv import load_dotenv
import telegram
import time

DEVMAN_API='https://dvmn.org/api/'

if __name__ == '__main__':
    load_dotenv(dotenv_path='.env')
    header = {'Authorization': f'Token {os.environ("DEVMAN_TOKEN")}'}
    bot = telegram.Bot(token=os.environ('TELEGRAM_BOT_TOKEN'))
    timestamp = None
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

                    bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message_text)
        except ReadTimeout:
            pass
        except ConnectionError:
            time.sleep(60)
        except HTTPError:
            bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text='Ошибка сервера!\nСервер времено не доступен!')
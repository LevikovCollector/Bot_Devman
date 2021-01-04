import requests
from requests.exceptions import ReadTimeout, HTTPError
import os
from dotenv import load_dotenv
import telegram

DEVMAN_API='https://dvmn.org/api/'

if __name__ == '__main__':
    load_dotenv(dotenv_path='.env')
    header = {'Authorization': f'Token {os.getenv("DEVMAN_TOKEN")}'}
    bot = telegram.Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))

    while True:
        try:
            response = requests.get(f'{DEVMAN_API}long_polling/', headers=header, timeout=95)
            response.raise_for_status()
            status = response.json()['status']
            if status == 'timeout':
                timestamp = response.json()['timestamp_to_request']
                request_param = {'timestamp': timestamp}
                response = requests.get(f'{DEVMAN_API}long_polling/', params=request_param,headers=header, timeout=95)
                response.raise_for_status()
            else:
                work_status = response.json()['new_attempts'][0]['is_negative']
                message_text = ''
                title = response.json()['new_attempts'][0]['lesson_title']
                url = f"https://dvmn.org{response.json()['new_attempts'][0]['lesson_url']}"
                if work_status:
                    message_text = f'У вас проверили работу «{title}»' \
                                   f'\nК сожалению нашлись ошибки.' \
                                   f'\nСсылка на урок: {url}'
                else:
                    message_text = f'У вас проверили работу «{title}»' \
                                   f'\nПреподавателю все понравилось, можно приступать к следующему уроку!' \
                                   f'\nСсылка на урок: {url}'

                bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message_text)
        except ReadTimeout:
            pass
        except ConnectionError:
            pass
        except HTTPError:
            bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text='Ошибка сервера!\nСервер времено не доступен!')
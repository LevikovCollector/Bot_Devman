import requests
import os
from dotenv import load_dotenv

DEVMAN_API='https://dvmn.org/api/'

if __name__ == '__main__':
    load_dotenv(dotenv_path='.env')
    header = {'Authorization': f'Token {os.getenv("DEVMAN_TOKEN")}'}
    response = requests.get(f'{DEVMAN_API}long_polling/', headers=header)
    print(response.json())
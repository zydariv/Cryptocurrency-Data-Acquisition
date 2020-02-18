import requests
import json
import ast
import pandas as pd
from matplotlib import pyplot as plt
import schedule
import time
import os


# minimum = 2
every_n_minutes = 3
first_state = True
API_KEY = ''
currencies = None
with open('config.json', 'r') as f:
    j = json.loads(f.read())
    API_KEY = j['API_KEY']
    currencies = j['currencies']
    bot_token = j['bot_token']
    bot_chatID = j['bot_chatID']


if not os.path.exists('data'):
    os.makedirs('data')


def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def fetch_data():
    jsons = []

    for curr in currencies:
        #LINK = f'https://min-api.cryptocompare.com/data/v2/histominute?fsym={curr}&tsym=EUR'
        LINK = f'https://min-api.cryptocompare.com/data/v2/histominute?fsym={curr}&tsym=EUR&limit={every_n_minutes-1}'
        headers = {'Authorization': 'Token' + API_KEY}

        r = requests.get(LINK, headers=headers)
        j = json.loads(r.text)
        jsons.append(j)

    for idx, j in enumerate(jsons):
        df_ = pd.DataFrame(j["Data"]["Data"])
        df_['time'] = pd.to_datetime(df_['time']*1000000000)

        global first_state
        if first_state:
            df_.to_csv(f'data/{currencies[idx]}.csv', mode='a')
        else:
            df_.to_csv(f'data/{currencies[idx]}.csv', mode='a', header=False)
    first_state = False
    telegram_bot_sendtext(str(df_['time']))


# Always run before new instance
schedule.clear()

# schedule.every().day.at("00:00").do(fetch_data)
s = schedule.every(60*every_n_minutes).seconds.do(fetch_data)

while True:
    schedule.run_pending()
    time.sleep(1)

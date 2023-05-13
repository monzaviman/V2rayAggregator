import requests
import base64
import sqlite3
import telegram
from time import  sleep
from telegram.constants import ParseMode
import asyncio

import tracemalloc
tracemalloc.start()

def base64_to_string(inp:str):
    return base64.b64decode(inp).decode('UTF-8')


def server_list_generator(servers:str):

    server_list = []

    for server in servers.split('\n'):
        server_list.append(server)

    return server_list

def insert_to_db(server):
    c = conn.cursor()
    c.execute("INSERT INTO servers (server) VALUES (?)",(server,))
    c.close()
    pass


def check_exist_in_db(server):
    c = conn.cursor()
    exists = c.execute("SELECT COUNT(*) FROM servers WHERE server=?",(server,)).fetchone()[0]
    if int(exists) == 1:

        c.close()
        return True


    elif int(exists) == 0:

        c.close()
        return False



def send_to_telegram(server_link:str):
    bot_token = '5260808018:AAEcUiHOnA3z2A2PeVp-9KrDFaTNaQ5hTWU'
    chat_id = '-1001643529458'
    html_message = f'🌟New V2ray Server!:\n\nType: {server_link.split("://")[0]}\n\n<b>Cick To Copy</b>\n\n<code>{server_link}</code>\n\n🛡 Anti-Censorship Project By @Secuner'
    post_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        "chat_id": chat_id,
        "text": html_message,
        "parse_mode": "HTML"
    }
    response = requests.post(post_url, data=payload)
    print(response.text)
    # print(server_link)

conn = sqlite3.connect('v2ray.db')
url = 'https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config.txt'
response = requests.get(url).text
servers = base64_to_string(response)
v2ray_results = server_list_generator(servers)
for link in v2ray_results:
    if check_exist_in_db(link) == True:
        continue
    elif check_exist_in_db(link) == False:
        insert_to_db(link)
        send_to_telegram(link)
        sleep(5)

conn.commit()
conn.close()
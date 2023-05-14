import requests
import base64
import sqlite3
from time import sleep
import tracemalloc
from subprocess import Popen, PIPE
from wget import download
from os.path import exists

tracemalloc.start()


def base64_to_string(inp: str):
    return base64.b64decode(inp).decode('UTF-8')


def server_list_generator(servers: str):
    server_list = []

    for server in servers.split('\n'):
        server_list.append(server)

    return server_list


def insert_to_db(server):
    c = conn.cursor()
    c.execute("INSERT INTO servers (server) VALUES (?)", (server,))
    c.close()
    pass


def check_exist_in_db(server):
    c = conn.cursor()
    exists = c.execute("SELECT COUNT(*) FROM servers WHERE server=?", (server,)).fetchone()[0]

    if int(exists) == 1:
        c.close()
        return True

    elif int(exists) == 0:
        c.close()
        return False


def send_to_telegram(server_link: str):
    bot_token = '5260808018:AAEcUiHOnA3z2A2PeVp-9KrDFaTNaQ5hTWU'
    chat_id = '-1001643529458'
    html_message = f'🌟New V2ray Server!:\n\nType: {server_link.split("://")[0]}\n\n<b>Cick To Copy</b>\n\n<code>{server_link}</code>\n\n🛡 Anti-Censorship Project By @Secuner'
    post_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        "chat_id": chat_id,
        "text": html_message,
        "parse_mode": "HTML"
    }
    res = requests.post(post_url, data=payload)
    print(res.text)
    # print(server_link)


def find_config(url: str, decode: bool = False):
    global conn

    conn = sqlite3.connect('v2ray.db')

    response = requests.get(url)

    if response.status_code == 200:
        response = response.text

        if decode:
            servers = base64_to_string(response)
        else:
            servers = response

        v2ray_results = server_list_generator(servers)

        for link in v2ray_results:
            if check_exist_in_db(link) is False:
                insert_to_db(link)
                send_to_telegram(link)
                speed_test(link)
                sleep(5)

        conn.commit()
        conn.close()


def check_vmess_cli():
    if exists("vmessspeed_amd64_linux") is False:
        download("https://github.com/v2fly/vmessping/releases/download/v0.3.4/vmessspeed_amd64_linux.zip")

        import zipfile

        with zipfile.ZipFile("vmessspeed_amd64_linux.zip") as file:
            file.extractall()

        from os import system

        system("chmod +x vmessspeed_amd64_linux")


def speed_test(server: str):
    check_vmess_cli()

    process = Popen(["./vmessspeed_amd64_linux", server], stdout=PIPE)
    result = process.communicate()[0]
    pass


def main():
    config_links_decode = [
        "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config.txt",
        "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity",
        "https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/sub_merge_base64.txt",
        "https://free.iam7.tk/vmess/sub",
        "https://proxy.yugogo.xyz/vmess/sub",
        "https://proxy.yiun.xyz/vmess/sub",
        "https://clash.myvm.cc/vmess/sub",
        "https://free.jingfu.cf/vmess/sub"
    ]

    config_links = [
        "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/splitted/vmess.txt",
    ]

    for link in config_links_decode:
        find_config(link, True)

    for link in config_links:
        find_config(link)


if __name__ == "__main__":
    main()

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from flask import Flask
import threading
import requests
import random
import time
import os

app = Flask(__name__)


def getNames():
    names = []
    firefoxOptions = Options()
    firefoxOptions.add_argument('--headless')
    driver = webdriver.Firefox(options=firefoxOptions)

    driver.get('https://chaturbate.com/?page=5')

    time.sleep(1)

    for i in driver.find_elements(By.TAG_NAME, 'a'):
        try:
            name = i.get_attribute('data-room')
            if name is not None and name not in names:
                names.append(name)
        except:
            pass

    return names


def checkCreatorOnline(creator):
    json_data = requests.get(f"https://chaturbate.com/api/chatvideocontext/{creator}").json()
    if json_data["room_status"] not in ["offline", "private"]:
        return True
    return False


def pullInfo(creator):
    try:
        json_data = requests.get('https://chaturbate.com/api/chatvideocontext/' + str(creator)).json()
    except:
        print('Exception, sleeping and trying again')
        time.sleep(13)
        json_data = requests.get('https://chaturbate.com/api/chatvideocontext/' + str(creator)).json()
    tUrl = 'https://roomimg.stream.highwebmedia.com/riw/'
    req = {}
    for i in json_data:
        if 'hls_source' in i:
            req.update({'hls_source': str(json_data[i])})
        elif 'room_title' in i:
            req.update({'room_title': str(json_data[i])})
        elif 'broadcaster_username' in i:
            req.update({'broadcaster_username': str(json_data[i])})
    req.update({'thumbnail_url': (tUrl + str(req.get('broadcaster_username')) + '.jpg')})
    return req


def gatherInfo(creator):
    print('Creator:', creator)
    t = pullInfo(creator)
    with open('dbtmp.txt', 'a', encoding='utf-8') as a:
        a.write(str(t) + '\n')


def run():
    while True:
        c = 0
        m = random.randint(25, 40)
        print('Fetching new names')
        for i in getNames():
            if c != m:
                gatherInfo(i)
                time.sleep(5)
                c += 1
        os.replace('dbtmp.txt', 'db.txt')
        print('Database updated')
        time.sleep(1800)


@app.route('/')
def server():
    with open('db.txt', 'r', encoding='utf-8') as a:
        data = a.readlines()
    return data


t1 = threading.Thread(target=app.run)
t2 = threading.Thread(target=run)

t1.start()
t2.start()

t1.join()
t2.join()

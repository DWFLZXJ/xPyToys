#!/usr/bin/env python
# encoding: utf-8
import random

import sys
import datetime
import re
import os
import time
reload(sys)
sys.setdefaultencoding('utf-8')
from weibo import Client

APP_KEY = '41*********26'  # app key
APP_SECRET = '4e***********520'  # app secret
CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'  # callback url
AUTH_URL = 'https://api.weibo.com/oauth2/authorize'
USERID = '18******0'  # userid
PASSWD = '*********'  # password


def post_new(content, pic, location):
    client = Client(APP_KEY, APP_SECRET, CALLBACK_URL, username=USERID, password=PASSWD)
    print client.post('statuses/upload', status=content, pic=pic, lat=location[0], long=location[1])


def gen_content(hour):
    if hour == 0:
        return u'新的一天已经到来~~~'
    if hour == 6:
        return u'早上好，该起床啦~~~'
    if hour == 8:
        return u'早饭时间~~~'
    if hour == 12:
        return u'中午好,该去吃午饭啦~~~'
    if hour == 18:
        return u'晚饭时间到，吃饭去~~~'
    if hour == 0:
        return u'好晚啊，该去睡觉啦~~~'
    if hour == 22:
        return u'去吃点宵夜，饿啦~~~'
    if 1 <= hour <= 5:
        return u'午夜时分，整点报时~~~'
    if 13 <= hour <= 17:
        return u'下午啦，旭哥的机器人整点报时~~~'
    if hour < 12:
        return u'旭哥的机器人要整点报时啦~~~'
    if hour == 19:
        return u'新闻联播时间，关注国家大事~~~'
    return u'晚间整点报时~~~'


def get_today():
    """
    gen a string like '20150520'
    """
    return time.strftime('%Y%m%d', time.localtime())


def gen_location():
    # -90 - +90
    # -180 - +180
    return random.randint(-90, 90), random.randint(-180, 180)

base = '/data/images/mzt/'
def get_img_path():
    for x in os.listdir(base):
        for y in os.listdir(base + x):
            return base + x + '/' + y


def post_hour_part():
    now_time = unicode(datetime.datetime.now())[:16]
    hour = map(int, re.findall(u'\\d+', now_time))[3]
    status = u'现在是' + now_time + u'，' + gen_content(hour) + u'妹子图来了~~~'
    img_path = get_img_path()
    post_new(status, open(img_path, 'rb'), gen_location())
    os.remove(img_path)


if __name__ == '__main__': 
    post_hour_part()


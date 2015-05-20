#!/usr/bin/env python
# encoding: utf-8
import random

import sys
import datetime
import re
import os
import time
from PIL import Image

reload(sys)
sys.setdefaultencoding('utf-8')
from weibo import Client

APP_KEY = ''  # app key
APP_SECRET = ''  # app secret
CALLBACK_URL = ''  # callback url
AUTH_URL = ''
USERID = ''  # userid
PASSWD = ''  # password


def post_new(content, pic, location):
    client = Client(APP_KEY, APP_SECRET, CALLBACK_URL, username=USERID, password=PASSWD)
    print client.post('statuses/upload', status=content, pic=pic, lat=location[0], long=location[1])


def gen_content(hour):
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


def part_of_image(path, hour):
    part_x = hour / 6
    part_y = hour % 6
    img = Image.open(path)
    x, y = img.size
    x, y = x/6, y/4
    box = (part_y * x, part_x * y, (1 + part_y) * x, (1 + part_x) * y)
    tmp_path = '/data/bing_bg/%s.jpg' % str(int(time.time()))
    img.crop(box).save(tmp_path)
    return tmp_path


def get_today():
    """
    gen a string like '20150520'
    """
    return time.strftime('%Y%m%d', time.localtime())


def gen_location():
    # -90 - +90
    # -180 - +180
    return random.randint(-90, 90), random.randint(-180, 180)


def post_hour_part():
    now_time = unicode(datetime.datetime.now())[:16]
    hour = map(int, re.findall(u'\\d+', now_time))[3]
    status = u'现在是' + now_time + u'，' + gen_content(hour) + u'下面是今天bing首页壁纸的第%d/24块(将在今天最后一分钟发布完整的图片)' % (hour + 1)
    part_img_path = part_of_image('/data/bing_bg/%s.jpg' % get_today(), hour)
    post_new(status, open(part_img_path, 'rb'), gen_location())
    os.remove(part_img_path)


def post_today_bing_bg():
    status = u'今天即将结束，把今天分成24份发出去的bing首页壁纸完整发一遍吧，晚安~~~'
    post_new(status, open('/data/bing_bg/%s.jpg' % get_today(), 'rb'), gen_location())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Argument wrong, need 2, got', len(sys.argv)
    elif sys.argv[1].strip() == 'hour':
        post_hour_part()
    elif sys.argv[1].strip() == 'end':
        post_today_bing_bg()
    else:
        print 'Unsupported argument :', sys.argv[1]

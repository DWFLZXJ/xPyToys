#!/usr/bin/env python
# -*- coding:utf-8 -*-
import codecs
import cookielib
import json

import sys
import urllib
import urllib2
import time
import datetime

reload(sys)
sys.setdefaultencoding("utf-8")

import re
import base64
import binascii
import rsa

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


def login_weibo(username, password):
    try:
        prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCal' \
                       'lBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.15)&_=1400822309846' % username
        pre_login_data = opener.open(prelogin_url).read().decode('utf-8')
        servertime = re.findall('"servertime":(.*?),', pre_login_data)[0]
        pubkey = re.findall('"pubkey":"(.*?)",', pre_login_data)[0]
        rsakv = re.findall('"rsakv":"(.*?)",', pre_login_data)[0]
        nonce = re.findall('"nonce":"(.*?)",', pre_login_data)[0]
        su = base64.b64encode(bytes(urllib.quote(username)))
        rsa_publickey = int(pubkey, 16)
        key = rsa.PublicKey(rsa_publickey, 65537)
        message = bytes(str(servertime) + '\t' + str(nonce) + '\n' + str(password))
        sp = binascii.b2a_hex(rsa.encrypt(message, key))
        param = {
            'entry': 'weibo',
            'gateway': 1,
            'from': '',
            'savestate': 7,
            'useticket': 1,
            'pagerefer': 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D',
            'vsnf': 1,
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': sp,
            'sr': '1680*1050',
            'encoding': 'UTF-8',
            'prelt': 961,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack'
        }
        data = urllib.urlencode(param).encode('utf-8')
        s = opener.open('http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)', data).read().decode('gbk')
        urll = re.findall("location.replace\(\'(.*?)\'\);", s)[0]
        opener.open(urll).read()

        return True
    except:
        return False


def post_weibo(content):
    if not login_weibo(USERNAME, PASSWORD):
        print 'login error, exit.'
        return
    post_data = urllib.urlencode({
        'location': 'v6_content_home',
        'appkey': '',
        'style_type': '1',
        'pic_id': '',
        'text': content,
        'pdetail': '',
        'rank': '',
        'module': 'stissue',
        'pub_type': 'dialog',
        '_t': '0',
    })
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://weibo.com/duxu0805/home?wvr=5',
    }
    url = 'http://weibo.com/aj/mblog/add?ajwvr=6&__rnd=' + str(int(time.time())) + '000'
    request = urllib2.Request(url, data=post_data, headers=headers)
    return opener.open(request).read()


def gen_content(now_time):
    time_part = map(int, re.findall(u'\\d+', now_time))

    if time_part[3] == 6:
        return u'早上好，该起床啦~~~'
    if time_part[3] == 8:
        return u'早饭时间~~~'
    if time_part[3] == 12:
        return u'中午好,该去吃午饭啦~~~'
    if time_part[3] == 18:
        return u'晚饭时间到，吃饭去~~~'
    if time_part[3] == 0:
        return u'好晚啊，该去睡觉啦~~~'
    if time_part[3] == 22:
        return u'去吃点宵夜，饿啦~~~'
    if 1 <= time_part[3] <= 5:
        return u'午夜时分，整点报时~~~'
    if 13 <= time_part[3] <= 17:
        return u'下午啦，旭哥的机器人整点报时~~~'
    if time_part[3] < 12:
        return u'旭哥的机器人要整点报时啦~~~'
    if time_part[3] == 19:
        return u'新闻联播时间，关注国家大事~~~'
    return u'晚间整点报时~~~'


def write_log(text):
    f = codecs.open('/data/weibo.log', 'a', 'utf-8')
    f.write(text)
    f.close()


def main():
    now_time = unicode(datetime.datetime.now())[:19]
    text = u'现在是' + now_time + u'，' + gen_content(now_time)
    if not json.loads(post_weibo(text))[u'code'] == u'100000':
        write_log(now_time + u'报时失败~~~\n')


if __name__ == '__main__':
    main()


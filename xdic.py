#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys, re, requests, json, urllib

ID = '6446269'
API_KEY = '*****************************'
SECRET_KEY = '*****************************''
URL = 'http://openapi.baidu.com/public/2.0/translate/dict/simple?client_id={0}&q={1}&from={2}&to={3}'

fmt = u'\033[0;3{}m{}\033[0m'.format


class Color(object):
    BLACK  = 0  # 黑
    RED    = 1  # 红
    GREEN  = 2  # 绿
    YELLOW = 3  # 棕
    BLUE   = 4  # 蓝
    PURPLE = 5  # 紫
    CYAN   = 6  # 青
    GRAY   = 7  # 灰


def translate(key, to=None):
    if re.match(ur'\w+', key):
        frm, to = 'en', 'zh'
    else:
        frm, to = 'zh', 'en'
    url = URL.format(API_KEY, urllib.quote(key), frm, to)
    data = json.loads(requests.get(url).content)
    if data['errno']:
        return None
    return data['data']


def print_pronu(data, key, color, desc):
    if key in data and data[key]:
        print fmt(color, u'    %s: [%s]' % (desc, data[key]))


def main():
    data = translate(sys.argv[1])
    # data = translate(key)
    print fmt(Color.RED, u'->{}:'.format(data['word_name']))
    symbols = data['symbols'][0]

    print_pronu(symbols, 'ph_am', Color.GREEN, u'美式发音')
    print_pronu(symbols, 'ph_en', Color.GREEN, u'英式发音')
    print_pronu(symbols, 'ph_zh', Color.GREEN, u'中文发音')

    for part in symbols['parts']:
        desc = part['part'].ljust(6) if part['part'] else ''
        print fmt(Color.BLUE, u'    {}  {}'.format(desc, u'  '.join(part['means'])))

if __name__ == '__main__':
    main()


#!/usr/bin/env python
# encoding=utf-8
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import sys
import re
import time
import datetime

from bs4 import BeautifulSoup
import requests


reload(sys)
sys.setdefaultencoding("utf-8")

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0',
}
HTML = u'''  
    <div class="container-fluid">
        <div class="row-fluid">
            <div class="span12">
                <h3>
                    <u>%s%s</u>-冉家坝租房推荐如下:
                </h3>
                <ol>
                    %s
                </ol>
            </div>
        </div>
    </div> 
'''


def calc_point(item):
    try:
        point = (2000 - item['price']) / 100.0
        point = (point, 5)[point >= 5]

        point += (item['area'] - 50) / 10.0

        if item['room_count'][0] == 3:
            point += 8

        if item['room_count'][1] == 2:
            point += 1
        if item['room_count'][2] == 2:
            point += 1

        t = item['pics_count'] / 10.0
        point += ((t, 0.5)[t > 0.5])

        p = eval(item['floor'] + '.0') * 10
        point += ((p, 5)[p > 5])

        if u'整租' in item['title']:
            point += 2
        if u'个人' in item['title'] or u'私人' in item['title']:
            point += 1.5
        
        point += item['pics_count']
        
        if u'祈年悦城' in item['village'] or u'海沁小区' in item['village'] or u'城市心筑' in item['village'] or u'尚源印象' in item['village']:
            point += 10

        return point * 5.0
    except Exception, e:
        print e
        return 0


def _parse_item(li):
    item = {
        'point': 0,
        'price': 0,
        'area': 0,
        'room_count': [],
        'floor': '',
        'village': '',
        'location': '',
        'title': '',
        'pics_count': 0,
        'link': '',
        'feature': []
    }
    price_info = li.find('div', attrs={'class': 'list-mod3'})
    try:
        item['price'] = int(price_info.find('em', attrs={'class': 'sale-price'}).getText())
    except:
        pass
    if not (1000 <= item['price'] <= 3000):
        return None
    try:
        item['area'] = float(re.findall('\\d+', price_info.find_all('p', attrs={'class': 'list-part'})[-1].getText())[0])
    except:
        pass
    if not 60.0 <= item['area'] <= 100:
        return None
    detail_info = li.find('div', attrs={'class': 'list-mod2'})
    house_info = detail_info.find('p', attrs={'class': 'list-word'})
    bedroom_cnt = re.findall(ur'(\d+)室(\d+)厅(\d+)卫', house_info.find('span', attrs={'class': 'js-huxing'}).getText())
    if bedroom_cnt[0] < 3:
        return None
    if len(bedroom_cnt) < 3:
        bedroom_cnt = bedroom_cnt + [0, 0]
    item['room_count'] = bedroom_cnt
    try:
        item['floor'] = re.findall(ur'(\d+?/\d+)层', house_info.getText())[0]
    except:
        pass
    try:
        item['feature'] = filter(lambda x: x.strip(), map(lambda s: s.getText(), detail_info.find('div', attrs={'class': 'lbl-box'}).find_all('span', attrs={'class': 'lbls'})))
    except:
        pass
    try:
        adds = detail_info.find('div', attrs={'class': 'list-word'}).find_all('span', attrs={'class': 'list-word-col'})
        adds = map(lambda add: add.getText().replace('\n', '').replace(' ', ''), adds)
        item['village'] = adds[0]
        item['location'] = adds[1]
    except:
        pass
    a = li.find('div', attrs={'class': 'info-title'}).find('a')
    item['title'] = a['title']
    if u'合租' in item['title'] or u'清水房' in item['title']:
        return None
    item['link'] = 'http://cq.ganji.com%s' % a['href']
    try:
        item['pics_count'] = int(li.find('div', attrs={'class': 'list-mod1'}).find('i', attrs={'class': 'number'}).getText())
    except:
        pass
    item['point'] = calc_point(item)
    return item


def parse_item(li):
    try:
        return _parse_item(li)
    except:
        return None


def gen_data(n):
    url = 'http://cq.ganji.com/fang1/ranjiaba/a1o%d/'
    data = []
    for x in xrange(1, n+1):
        time.sleep(0.5)
        data += filter(lambda x: x, map(lambda x: parse_item(x), BeautifulSoup(requests.get(url % x, headers=headers).content).find_all('li', attrs={'class': 'list-img clearfix'})))
    return data


def send_mail(items):
    today = time.strftime('%Y年%m月%d日')
    times = (u'上午', u'下午')[datetime.datetime.now().hour > 12]
    h = ''
    for item in items:
        if item['pics_count']:
            pic = u'; %d图' % item['pics_count']
        else:
            pic = u''
        h += (u'<li><a href="%s" target="_blank">%s</a> : [%d/月; %s; %s-%s%s]</li>' % (item['link'], item['title'], item['price'], item['floor'], item['location'].replace(u'冉家坝租房-', u''), item['village'], pic))
    html = HTML % (today, times, h)

    me = "搜房机器人<xxxxxxx@sina.com>"
    msg = MIMEText(html, _subtype='html', _charset='utf-8')
    msg['Subject'] = Header(u'%s%s冉家坝租房推荐' % (today, times), 'utf-8')
    msg['From'] = me
    msg['To'] = "" 
    try:
        server = smtplib.SMTP()
        server.connect("smtp.sina.com")
        server.login("xxxxxxx", "xxxxxxx")
        server.sendmail(me, [], msg.as_string()) 
        server.close()
        return True
    except Exception, e:
        print e
        return False


def main():
    cmped = lambda d1, d2: cmp(d2['point'], d1['point'])
    data = sorted(gen_data(10), cmp=cmped)
    pos = (5, len(data)-1)[len(data) < 3]
    send_mail(data[:pos])

if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding:utf-8 -*-
import copy
import json
import urllib
from bs4 import BeautifulSoup
import requests
import sys
import re
import time
from util import *

reload(sys)
sys.setdefaultencoding("utf-8")


class ZhCrawler(object):
    URL = 'http://www.zhihu.com/people/%s/'
    DETAIL_URL = 'http://www.zhihu.com/people/%s/about'
    FORMAT = {
        '_id': '',
        'url': '',
        'weibo': '',
        'nickname': '',
        'desc_single': '',
        'description': '',
        'fans': 0,
        'follow': 0,
        'askCount': 0,
        'answerCount': 0,
        'zhuanlanCnt': 0,
        'collectionCnt': 0,
        'editCount': 0,
        'agreed': 0,
        'thanked': 0,
        'collected': 0,
        'shared': 0,
        'jobs': [],
        'address': [],
        'educations': [],
        'viewCount': 0,
        'avatar': {'url': '', 'detail': []},
        'gender': '',
    }

    @classmethod
    def deal_str(cls, string):
        return re.sub(ur'\t|\r|\n', ' ', string).strip()

    def __init__(self):
        self.request = requests.Session()
        self.request.headers[
            'User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
        self.request.headers['Accept-Language'] = 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'
        self.request.headers['Connection'] = 'keep-alive'
        self.request.headers['Cookie'] = get_cookie()

    def get(self, url, deep=0):
        if deep == 3:
            return None
        time.sleep(0.3)
        try:
            return self.request.get(url).content
        except:
            return self.get(url, deep + 1)

    @classmethod
    def parse_nickname(cls, soup):
        if not soup:
            raise Exception('no nickname find.')
        try:
            desc = ZhCrawler.deal_str(soup.find('span', attrs={'class': 'bio'})['title'])
        except:
            desc = ''
        try:
            nick = ZhCrawler.deal_str(soup.find('a', attrs={'class': 'name'}).getText())
        except:
            nick = ZhCrawler.deal_str(soup.find('span', attrs={'class': 'name'}).getText())
        return nick, desc

    @classmethod
    def parse_weibo(cls, soup):
        return None if not soup else soup['href']

    @classmethod
    def parse_nums(cls, soup, count):
        if not soup:
            return [0 for _ in xrange(count)]
        data = map(int, re.findall(ur'\d+', soup.getText()))
        if len(data) == count:
            return data
        return [0 for _ in xrange(count)]

    @classmethod
    def parse_jobs(cls, soup):
        if not soup:
            return []
        lst = []
        for li in soup.find_all('li'):
            lst.append(ZhCrawler.deal_str(li.getText()))
        return lst

    def find_following(self, uid):
        lst = []
        if not uid:
            return lst
        url = 'http://www.zhihu.com/people/%s/followees' % uid
        content = self.get(url)
        if not content:
            return []
        soup = BeautifulSoup(content)
        for item in soup.find_all('div', attrs={'class': 'zm-profile-card zm-profile-section-item zg-clear no-hovercard'}):
            try:
                lst.append({'_id': item.find('a')['href'].replace('/people/', '')})
            except:
                pass
        return lst

    def crawl_one(self, uid):
        url = self.DETAIL_URL % uid
        content = self.get(url)
        soup = BeautifulSoup(content, 'html5lib')
        result = copy.deepcopy(self.FORMAT)
        result['url'] = self.URL % uid
        result['_id'] = uid
        result['weibo'] = self.parse_weibo(soup.find('a', attrs={'class': 'zm-profile-header-user-weibo'}))
        result['nickname'], result['desc_single'] = self.parse_nickname(soup.find('div', attrs={'class': 'title-section ellipsis'}))
        try:
            result['description'] = self.deal_str(soup.find('div', attrs={'class': 'zm-profile-header-description editable-group '}).find('span', attrs={'class': 'content'}).getText())
        except Exception, e:
            print e
        result['follow'], result['fans'] = self.parse_nums(soup.find('div', attrs={'class': 'zm-profile-side-following zg-clear'}), 2)
        result['askCount'], result['answerCount'], result['zhuanlanCnt'], result['collectionCnt'], result['editCount'] = self.parse_nums(soup.find('div', attrs={'class': 'profile-navbar'}), 5)

        detail = soup.find('div', attrs={'class': 'zm-profile-section-list zm-profile-details'})
        if detail:
            for index, div in enumerate(detail.find_all('div', attrs={'class': 'zm-profile-module'})):
                if index == 0:
                    result['agreed'], result['thanked'], result['collected'], result['shared'] = self.parse_nums(detail.find('div', attrs={'class': 'zm-profile-module zm-profile-details-reputation'}), 4)
                elif index == 1:
                    result['jobs'] = self.parse_jobs(div.find('ul', attrs={'class': 'zm-profile-details-items'}))
                elif index == 2:
                    result['address'] = self.parse_jobs(div.find('ul', attrs={'class': 'zm-profile-details-items'}))
                elif index == 3:
                    result['educations'] = self.parse_jobs(div.find('ul', attrs={'class': 'zm-profile-details-items'}))
        result['viewCount'] = int(soup.find_all('span', attrs={'class': 'zg-gray-normal'})[-1].find('strong').getText())
        try:
            result['gender'] = (u'F', u'M')['icon-profile-male' in soup.find('span', attrs={'class': 'item gender'}).find('i')['class']]
        except:
            pass
        try:
            img_url = 'http:' + soup.find('img', attrs={'class': 'avatar avatar-l'})['src']
            result['avatar']['url'] = img_url
            result['avatar']['detail'] = parse_age(img_url)
        except Exception, e:
            print e

        return result, self.find_following(uid)

    def run(self):
        for _ in xrange(3):
            self._run()
            # time.sleep(60)
            # TODO delete
            break

    def _run(self):
        uid = gen_todo_id()['_id']
        errtimes = 0
        while uid:
            if errtimes > 10:
                break
            print 'now uid :', uid
            try:
                self_info, todos = self.crawl_one(uid)
                print self_info, todos
                insert_todo_user(todos)
                insert_done_user(self_info)
            except Exception, e:
                print '_run', e
                errtimes += 1
                pass
            uid = gen_todo_id()['_id']
            time.sleep(0.5)


def parse_age(url):
    lst = []
    url = urllib.quote(url)
    url = 'http://apicn.faceplusplus.com/v2/detection/detect?api_key=230f413fecfaa462ca5f02f8760d28fc&api_secret=YiupnWTkbAhxBTg-9Xb-EBPMulbbTMjk&url=%s&attribute=gender,age' % url
    avatar_info = json.loads(requests.get(url).content)
    if 'error' in avatar_info:
        return lst
    for face in avatar_info['face']:
        face_attr = face['attribute']
        lst.append({
            'gender': face_attr['gender']['value'][0],
            'age': face_attr['age']['value'],
            'range': face_attr['age']['range'],
        })
    return lst


def main():
    ZhCrawler().run()


if __name__ == '__main__':
    main()

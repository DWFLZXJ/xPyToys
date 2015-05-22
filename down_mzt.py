#!/usr/bin/env python
# encoding: utf-8
import os
import urllib2
import sys
import time
import re

from bs4 import BeautifulSoup


reload(sys)
sys.setdefaultencoding('utf-8')

BASE_URL = 'http://www.meizitu.com/a/list_1_%d.html'
index_img_arch_pattern = re.compile('<h3 class="tit"><a href="(.+?)".+?>(.+?)<.+?/h3>')
headers = {}


def get_url_content(url):
    time.sleep(0.5)
    return urllib2.urlopen(urllib2.Request(url=url, headers=headers)).read()


def parse_img_index_page(url):
    content = get_url_content(url)
    res = []
    for url, name in re.findall(index_img_arch_pattern, content):
        name = name.strip().replace('<b>', '').decode('GB2312', 'ignore').encode('utf-8')
        res.append({
            'title': name,
            'url': url
        })
    return res


def download_a_img_page(item):
    url = item['url']
    title = item['title']

    save_path = '/data/images/mzt/%s/' % title
    if os.path.exists(save_path):
        return False
    os.makedirs(save_path)

    content = get_url_content(url)
    for index, imgitem in enumerate(BeautifulSoup(content).find('div', attrs={'id': 'picture'}).find_all('img')):
        u = imgitem['src'].strip()
        img_save_path = '%s%03d%s' % (save_path, index, u[-4:])
        if os.path.exists(img_save_path):
            continue
        img_content = get_url_content(u)
        with open(img_save_path, 'wb') as img_file:
            img_file.write(img_content)
        print 'saved', u, ',', img_save_path
    return True


def find_img_archs(check):
    err_conunt = 0
    page = 1
    saved = 0
    while True:
        try:
            url = BASE_URL % page
            result = parse_img_index_page(url)
            for item in result:
                try:
                    if not download_a_img_page(item):
                        saved += 1
                except:
                    pass
            if saved > 5 and check:
                break
            page += 1
        except:
            err_conunt += 1
            if err_conunt > 10 and check:
                break

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Argument count error, need 2, got', len(sys.argv)
    elif sys.argv[1].strip() == 'check':
        find_img_archs(True)
    elif sys.argv[1].strip() == 'all':
        find_img_archs(False)
    else:
        print 'Wrong argument.'


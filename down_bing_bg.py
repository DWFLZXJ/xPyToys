#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import os
import sys
import time

from qiniu import *
import requests


reload(sys)
sys.setdefaultencoding("utf-8")

ACCESS_KEY = 'QINIU ACCESS KEY'
SECRET_KEY = 'QINIU SECRET KEY'


def get_bing_img_json():
    url = 'http://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&nc=%s&pid=hp' % (str(int(time.time())) + '000')
    return json.loads(requests.get(url).content)


def find_img(json_data):
    image = json_data['images'][0]
    return image['url'], image['copyright']


def get_today():
    """
    gen a string like '20150520'
    """
    return time.strftime('%Y%m%d', time.localtime())


def download_image(img_url, file_path):
    """
    download image from a url, save to file_path
    """
    try:
        if not file_path.endswith('/'):
            file_path += '/'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        suffix = img_url[img_url.rfind('.'):]
        img_content = requests.get(img_url).content
        fname = file_path + get_today() + suffix
        with open(fname, 'wb') as img_file:
            img_file.write(img_content)
        return fname
    except:
        return ''


def push_2_qiniu(file_path):
    """
    push image file to qiniu
    """
    try:
        q = Auth(ACCESS_KEY, SECRET_KEY)
        token = q.upload_token('duxu-info', file_path)
        ret, info = put_file(token, file_path, file_path, mime_type="image/jpeg", check_crc=True)
        return str(info).find(u'Response [200]') >= 0
    except:
        return False


if __name__ == '__main__':
    img_url, intro = find_img(get_bing_img_json())
    saved_path = download_image(img_url, '/data/bing_bg/')
    push_2_qiniu(saved_path)


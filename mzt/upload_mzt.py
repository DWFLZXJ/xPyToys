#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import os

from qiniu import *


reload(sys)
sys.setdefaultencoding("utf-8")

ACCESS_KEY = '3n*************************************b'
SECRET_KEY = 'A**************************************9'


def push_2_qiniu(file_path):
    """
    push image file to qiniu
    """
    try:
        q = Auth(ACCESS_KEY, SECRET_KEY)
        token = q.upload_token('xvps', file_path)
        ret, info = put_file(token, file_path, file_path, mime_type="text/plain", check_crc=True)
        return str(info).find(u'Response [200]') >= 0
    except:
        return False

BATH_PATH = '/data/images/mzt/'


def write_log(msg, status):
    print status, ':', msg
    f_path = ('/data/log/mzt.fail.log', '/data/log/mzt.ok.log')[status]
    with open(f_path, 'a') as log_file:
        log_file.write('%s\n' % msg)


def upload_a_dir(path):
    now_path = BATH_PATH + path
    if not os.path.isdir(now_path):
        return
    for image in os.listdir(BATH_PATH + path):
        try:
            image_path = now_path + '/' + image
            if not push_2_qiniu(image_path):
                raise Exception
            write_log(image_path, True)
        except:
            write_log(image_path, False)


def upload():
    for path in os.listdir(BATH_PATH):
        upload_a_dir(path)

if __name__ == '__main__':
    upload()


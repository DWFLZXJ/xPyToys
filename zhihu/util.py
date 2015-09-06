#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import ConfigParser
import pymongo

reload(sys)
sys.setdefaultencoding("utf-8")

conf = ConfigParser.ConfigParser()
try:
    conf.readfp(open('conf/global.conf', "rb"))
except:
    conf.readfp(open('zhihu/conf/global.conf', "rb"))


def get_mongo_conf():
    return conf.get("global", "MONGO_HOST"), conf.getint("global", "MONGO_PORT")


def get_cookie():
    return conf.get('zhihu', 'COOKIE')


MONGO_CONF = get_mongo_conf()
MONGO_CONN = pymongo.MongoClient(MONGO_CONF[0], MONGO_CONF[1])


def gen_todo_id():
    try:
        coll = MONGO_CONN['zhihu']['todos']
        uid = coll.find_one()
        if uid:
            coll.delete_one(uid)
        return uid
    except Exception, e:
        print 'gen_todo_id', e
        return False


def _is_exists_in_db(filter, collection):
    try:
        return MONGO_CONN['zhihu'][collection].find_one(filter)
    except Exception, e:
        print '_is_exists_in_db', e
        return False


def insert_todo_user(todos_list):
    for todo in todos_list:
        try:
            filter = {'_id': todo['_id']}
            if _is_exists_in_db(filter, 'todos'):
                continue
            if _is_exists_in_db(filter, 'done'):
                continue
            MONGO_CONN['zhihu']['todos'].insert_one(todo)
        except Exception, e:
            print 'insert_todo_user', e
            pass


def insert_done_user(user):
    try:
        MONGO_CONN['zhihu']['done'].update_one({'_id': user['_id']}, {'$set': user}, True)
    except Exception, e:
        print 'insert_done_user', e
        pass


def main():
    print gen_todo_id()


if __name__ == '__main__':
    main()

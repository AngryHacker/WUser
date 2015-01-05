#!/usr/bin/env python
# encoding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import torndb


HOSTNAME = 'localhost'
USERNAME = 'houyf'
PASSWORD = 'Beyond'
DATABASE = 'xinan'

try:
    db = torndb.Connection(HOSTNAME, DATABASE, USERNAME, PASSWORD)
    db.execute('set names utf8')
    fp = open('evil1.txt', 'r')
    lines = fp.readlines()
    for i in lines:
        pos = i.find('/u/')
        pos += 3
        accountId = i[pos:]
        sql = 'insert into users(user_id) values(%s)'
        try :
            db.execute(sql,  accountId)
            print 'insert %s successful'%accountId
        except torndb.MySQLdb.Error, e:
            print 'fail to insert %s' %accountId
except torndb.MySQLdb.Error, e:
    print e.args[1]
    exit(1)

exit(0)

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
        sql1 = 'insert into users(user_id) values(%s)'
        sql2 = 'update users set is_evil=1 where user_id=%s'
        try :
            #开启事务
            db.execute('start transaction')
            db.execute(sql1,  accountId)
            print 'insert %s successful'%accountId
            db.update(sql2, accountId)
            #提交事务
            db.execute('commit')
        #如果遇到问题需要回滚事务
        except torndb.MySQLdb.Error, e:
            print 'fail to insert %s' %accountId
            db.execute('rollback')
except torndb.MySQLdb.Error, e:
    print e.args[1]
    exit(1)

exit(0)

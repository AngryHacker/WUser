#!/usr/bin/python
# encoding: utf-8

import concern
import MySQLdb

db = MySQLdb.connect(host="localhost", user="houyf", passwd="Beyond", db="weibo")
cursor = db.cursor()
cursor.execute('set names "utf8"')
cursor.execute("select id from user where getConcern = 0 ")
userTable = cursor.fetchall()
users = {}
print len(userTable)
for row in userTable:
    print row[0]
    users = concern.getConcernByUid(row[0])
    try :
        sql = 'update user set getConcern = ' + '1' + ' where id = ' + str(row[0])
        cursor.execute(sql)
        db.commit()
    except Exception, e:
        print e[0], e[1]

    for id in users :
        try:
            sql =  'insert into user(`id`, `nickname` ) values(%s, "%s")' % (str(id), str(users[id]) )
            cursor.execute(sql)
            db.commit()
        except Exception, e:
            print e[0], e[1]
        else:
            print sql

cursor.close()
db.close()

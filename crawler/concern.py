#!/usr/bin/python
# encoding: utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import urllib2
import time
from bs4 import BeautifulSoup
import MySQLdb
import socket
import json

#config
socket.setdefaulttimeout(10.0)
FP_COOKIE = open("/home/houyf/WUser/crawler/cookies.txt","r")
ARGS_COOKIE = FP_COOKIE.readline()
FP_COOKIE.close()
MY_UID = "3170483413";

#fetch html
def fetchUrl(url):
    try:
        request = urllib2.Request(url);
        request.add_header('Cookie',ARGS_COOKIE)
        response = urllib2.urlopen(request)
        return response.read()
    except :
        # print '[error]Fetch html fail '
        print sys.exc_info()
        return ''

#存放到文件中
def File(html):
    try:
        fp = open('content.html', 'w')
        fp.write(html)
        fp.close()
    except Exception, e:
        print e[0], e[1]


def getPids(html):
    left = html.find('Pl_Official_HisRelation__') + len('Pl_Official_HisRelation__')
    right = left +2
    return html[left:right]

def getConcernByHtml(html):
    left = html.find('{')
    right = html.find('}',len(html) - 100) + 1
    html = html[left:right]
    try:
        jsonData  = json.loads(html)
    except:
        return {}
    html = jsonData['html']
    filter = {'\\r\\n':'\r\n', '\\t':'\t','\\/': '/', '\\"':'"' }
    for key in filter.keys():
        html = html.replace(key, filter[key])
    File(html)
    soup = BeautifulSoup(html)
    divList = soup.findAll('li','follow_item S_line2' )

    #select all the user's  concern
    concern ={}
    for div in divList :
        str = div['action-data']
        str = str.split('&')
        id = str[0].split('=')[1]
        name = str[1].split('=')[1]
        concern[id] = name
    return concern

def getConcernByUid(uid):

    concern_url = 'http://weibo.com/'+ str(uid) + '/follow?page='
    page = 1
    concern_url += str(page)
    html = fetchUrl(concern_url)
    concern_url =  'http://weibo.com/'+ str(uid) + '/follow? \
        &ajaxpagelet=1 \
        &pids=Pl_Official_HisRelation__' + getPids(html) + '&page='
    users = {}
    count = 0
    for page in xrange(1,20):
        html = fetchUrl(concern_url + str(page))
        if(html == '') :
            if(count == 2) :
                return users
            count += 1
            continue
        concern = getConcernByHtml(html)
        users.update(concern)
    return users


def insert_user(user_id, nickname, cursor):
    try:
        sql = 'insert into users(`user_id`, `nickname`) values(%s, "%s")' % (str(user_id), str(nickname))
        cursor.execute(sql)
    except:
        print sys.exc_info()
    db.commit()

def insert_fans(user1, user2, cursor):
    try:
        sql = 'insert into fans(`user1`, `user2`) values(%s, %s)' %(str(user1), str(user2))
        cursor.execute(sql)
    except:
        print sys.exc_info()
    db.commit()


if(__name__ == '__main__'):

    #连接数据库和预处理
    db = MySQLdb.connect(host='localhost', user='houyf', passwd='Beyond', db='xinan')
    cursor = db.cursor()
    cursor.execute('set names utf8')
    #获取用户列表
    sql = 'select user_id from users where is_fetch_concern=0 and is_evil=0'
    cursor.execute(sql)
    msg = cursor.fetchall()
    for row in msg:
        user_id = row[0]
        print 'fetch concern of %s now ...' %user_id
        users = getConcernByUid(user_id)
        for i in users :
            insert_user(i, users[i], cursor)
            insert_fans(user_id, i, cursor)
        #标记该用户已经被抓取
        sql = 'update users set is_fetch_concern = 1 where user_id=%s' %user_id
        cursor.execute(sql)
        db.commit()
    cursor.close()
    db.close()


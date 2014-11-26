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
    except:
        print '[error]Fetch html fail'
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
    # filter which related to SUN YAT-SEN
    # users = {}
    # for id in concern:
        # if(concern[id].find('中大') >= 0):
            # users[id] = concern[id]
        # elif (concern[id].find('中山大学')>= 0):
            # users[id] = concern[id]
    # return users

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
    for page in xrange(1,2):
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
    user_id = "1705586121"
    users = getConcernByUid(user_id)
    db = MySQLdb.connect(host='localhost', user='houyf', passwd='Beyond', db='xinan')
    cursor = db.cursor()
    cursor.execute('set names utf8')

    for i in users :
        # insert_user(i, users[i], cursor)
        insert_fans(i, user_id, cursor)
    cursor.close()
    db.close()


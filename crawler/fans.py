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

    # 从html中的script中解析出关于粉丝的html部分
    while html.find('<script>') != -1:
        pos = html.find('<script>')
        pos += len('<script>')
        html = html[pos:]
    left = html.find('"html":"') + len('"html":"')
    right = html.find('"})</script>')
    print 'from %s to %s'% (left, right)
    html = html[left:right]
    # 处理转义
    filter = {'\\r\\n':'\r\n', '\\t':'\t','\\/': '/', '\\"':'"' }
    for key in filter.keys():
        html = html.replace(key, filter[key])
    # 提取出带有uid和nickname
    soup = BeautifulSoup(html)
    divList = soup.findAll('li','follow_item S_line2' )
    concern ={}
    for div in divList :
        str = div['action-data']
        str = str.split('&')
        id = str[0].split('=')[1]
        name = str[1].split('=')[1]
        concern[id] = name
    return concern

#内容写入文件
def write_to_file(filename, content):
    fp = open(filename, 'w')
    fp.write(content)
    fp.close()

#浏览器打开
import webbrowser
def view(path):
    webbrowser.open(path)

#获取相关长ID
def GetAccountId(uid) :
    url = "http://weibo.com/u/" + str(uid)
    html =  fetchUrl(url)
    filter = {'\\r\\n':'\r\n', '\\t':'\t','\\/': '/', '\\"':'"' }
    for key in filter.keys():
        html = html.replace(key, filter[key])
    left = html.find('page_id') +  len("page_id']='")
    right = html.find("'",left )
    return  html[left:right]

#通过用户的短ID来获取像一个的粉丝列表
def getConcernByUid(uid):
    concern_url = 'http://weibo.com/p/'+ GetAccountId(uid) + '/follow?relate=fans&page='
    users = {}
    count = 0
    for page in xrange(1,10):
        html = fetchUrl(concern_url + str(page))
        if(html == '') :
            if(count == 2) :
                return users
            count += 1
            continue
        concern = getConcernByHtml(html)
        users.update(concern)
    return users

#插入新抓取的用户数据
def insert_user(user_id, nickname, cursor):
    try:
        sql = 'insert into users(`user_id`, `nickname`) values(%s, "%s")' % (str(user_id), str(nickname))
        cursor.execute(sql)
    except:
        print '用户%s 已经被抓取了'% str(nickname)
    db.commit()

#建立起被抓取用户和其粉丝的关系
def insert_fans(user1, user2, cursor):
    try:
        sql = 'insert into fans(`user1`, `user2`) values(%s, %s)' %(str(user1), str(user2))
        cursor.execute(sql)
    except:
        print '用户%s 和 %s的关系粉丝已经存在'% (str(user1), str(user2))
    db.commit()


if(__name__ == '__main__'):

    #连接数据库和预处理
    db = MySQLdb.connect(host='localhost', user='houyf', passwd='Beyond', db='xinan')
    cursor = db.cursor()
    cursor.execute('set names utf8')
    #获取已有的用户列表
    sql = 'select user_id from users where is_fetch_fans=0'
    cursor.execute(sql)
    msg = cursor.fetchall()
    #取得每个用户的一定量的粉丝
    for row in msg:
        user_id = row[0]
        print 'fetch concern of %s now ...' %user_id
        users = getConcernByUid(user_id)
        for i in users :
            insert_user(i, users[i], cursor)
            insert_fans(i, user_id, cursor)
        sql = 'update users set is_fetch_fans = 1 where user_id=%s'% user_id
        cursor.execute(sql)
        db.commit()
    cursor.close()
    db.close()


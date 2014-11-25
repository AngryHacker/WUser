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
FP_COOKIE = open("/home/houyf/python/wCrawler/cookies.txt","r")
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
    jsonData  = json.loads(html)
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

    #filter which related to SUN YAT-SEN
    users = {}
    for id in concern:
        if(concern[id].find('中大') >= 0):
            users[id] = concern[id]
        elif (concern[id].find('中山大学')>= 0):
            users[id] = concern[id]
    return users

def getConcernByUid(uid):

    concern_url = 'http://weibo.com/'+ str(uid) + '/follow?page='
    page = 1
    concern_url += str(page)
    html = fetchUrl(concern_url)
    concern_url =  'http://weibo.com/'+ str(uid) + '/follow? \
        &ajaxpagelet=1 \
        &pids=Pl_Official_HisRelation__' + getPids(html) + '&page='
    users = {}
    for page in xrange(1,10):
        html = fetchUrl(concern_url + str(page) )
        concern = getConcernByHtml(html)
        users.update(concern)
    return users

# -*- coding: utf-8 -*-
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


#class: User
class User:
    def __init__(self):
        self.id = 0
        self.accountID = ''
        self.domain = ''
#class: Weibo
class Weibo:
    def __init__(self):
        self.weiboID = ''
        self.uid = ''
        self.content = ''
        self.pubTime = ''

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

#get accountID from html
def getAccountID(html):
    start = html.find('pftb_ul') - 12
    end = html.find('/ul>', start) + 4
    weiboTab = html[start:end]
    weiboTab = weiboTab.replace("\\t","\t")
    weiboTab = weiboTab.replace("\\r\\n","")
    weiboTab = weiboTab.replace("\\/","/")
    weiboTab = weiboTab.replace('\\"','"')
    soup = BeautifulSoup(weiboTab)
    aList = soup.findAll('a');
    if len(aList) == 0:
        return "0";
    else:
        reg = re.compile('^.+?\/p\/(?P<accountID>[^ ]*)\/home.+?')
        regMatch = reg.match(str(aList[0]))
        try:
            linebits = regMatch.groupdict()
        except:
            return "0"
        return linebits['accountID']

#get weibo list from html
def getWeiboList(html, uid):
    try:
        decodejson = json.loads(html)
        weiboDiv = decodejson['data']
    except:
        return []
    weiboDiv = weiboDiv.replace("\\t","\t")
    weiboDiv = weiboDiv.replace("\\r\\n","")
    weiboDiv = weiboDiv.replace("\\/","/")
    weiboDiv = weiboDiv.replace('\\"','"')
    soup = BeautifulSoup(weiboDiv);
    divList = soup.findAll('div', 'WB_feed_type')
    weiboList = []
    for eachDiv in divList:
        tmpWeibo = Weibo()
        tmpWeibo.uid = uid
        #get mid first
        reg = re.compile('^.+?mid="(?P<mid>[^ ]*)".+?')
        regMatch = reg.match(str(eachDiv))
        try:
            linebits = regMatch.groupdict()
            tmpWeibo.weiboID =  str(linebits['mid'])
        except:
            continue
        #get content
        deList = eachDiv.findAll('div', 'WB_text')
        for eachDe in deList:
            for eachContent in eachDe.contents:
                tmpWeibo.content += str(eachContent)
        #get pubtime
        pubtime = eachDiv.find(date=True)
        tmpWeibo.pubTime = str(dict(pubtime.attrs)['title'])
        print  tmpWeibo.pubTime ;#exit()
        weiboList.append(tmpWeibo)
    return weiboList


def GetAccountId(uid) :
    url = "http://weibo.com/u/" + str(uid)
    html =  fetchUrl(url)

    filter = {'\\r\\n':'\r\n', '\\t':'\t','\\/': '/', '\\"':'"' }
    for key in filter.keys():
        html = html.replace(key, filter[key])
    left = html.find('page_id') +  len("page_id']='")
    right = html.find("'",left )
    return  html[left:right]

#connect db
db = MySQLdb.connect(host="localhost", user="houyf", passwd="Beyond", db="xinan")
cursor = db.cursor()
cursor.execute('set names "utf8"')
#config
socket.setdefaulttimeout(10.0)
FP_COOKIE = open("/home/houyf/WUser/crawler/cookies.txt","r")
ARGS_COOKIE = FP_COOKIE.readline()
FP_COOKIE.close()
MY_UID = "3170483413";
#read user from database
cursor.execute("select user_id, domain from users where is_fetch = 0 and is_evil=0")
userTable = cursor.fetchall()
for row in userTable:
    #each user, accountID is needed
    tmpUser = User()
    tmpUser.id = str(row[0])
    tmpUser.domain = str(row[1])
    tmpUser.accountID = tmpUser.domain + tmpUser.id

    if tmpUser.domain == "0":
        time.sleep(2)
        print '[info]User: ' + tmpUser.id + 'has no domain. Get it now'
        FOLLOW_INIT_PATH = "http://weibo.com/u/" + tmpUser.id
        rawcontents = fetchUrl(FOLLOW_INIT_PATH)
        tmpUser.accountID = GetAccountId(tmpUser.id);
        if(not tmpUser.accountID.isdigit()):
            # print tmpUser.accountID
            print 're has some problem'
            continue
        tmpUser.domain = str(tmpUser.accountID)[0:6]
        if tmpUser.accountID == "0":
            '[warning]get accountID fail.'
            continue
        # save the  accountID
        try :
            sql = "update users " + "set domain = " + str(tmpUser.domain) + " where user_id = " + str(tmpUser.id) ;
            print sql
            tmp = cursor.execute(sql);
            db.commit()
            print tmp;
        except Exception, e:
            print "Error %s: %s" %(e[0], e[1])
            db.rollback()

    eachUser = tmpUser
    # init PATH
    PATH_REAL = "http://weibo.com/p/aj/v6/mblog/mbloglist?id=" + eachUser.accountID + "&domain=" + eachUser.domain + "&page="
    allWeiboList = []
    #fetch 200 page in default
    failTimes = 0
    for page in range(1,20):

        print '[info]Fetch Page ' + str(page)
        request = urllib2.Request(PATH_REAL + str(page))
        request.add_header('Cookie',ARGS_COOKIE)
        try:
            response = urllib2.urlopen(request)
            rawcontents = response.read()
        except:
            print '[error] Url Read Fail.'
            continue
        tmpList = getWeiboList(rawcontents, eachUser.id)
        print '[info]Num of weibo: ' + str(len(tmpList))
        if len(tmpList) == 0:
            failTimes = failTimes + 1
            if failTimes >= 3:
                print '[info]Fetch user:' + eachUser.id + ' end.'
                break
        else:
            allWeiboList.extend(tmpList)
    #update db
    print '[info]Fetch end. Total fetch: ' + str(len(allWeiboList))
    for eachWeibo in allWeiboList:
        sql = "insert into post values(%s,%s,%s,%s)"
        try:
            cursor.execute(sql, [eachWeibo.weiboID, eachWeibo.uid, eachWeibo.content, eachWeibo.pubTime])
        except Exception,data:
            print data
            print '[error]insert weibo fail'
            continue

    sql = "update users set is_fetch = 1, domain = " + eachUser.domain + " where user_id = " + eachUser.id
    cursor.execute(sql)
    db.commit()

#close db
cursor.close()
db.close()

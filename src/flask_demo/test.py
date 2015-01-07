#!/usr/bin/env python
# coding=utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb
import chardet
from sklearn import svm
from sklearn.externals import joblib
from bs4 import BeautifulSoup
import jieba.posseg as pseg
import re
import urllib2
import time
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
    FP_COOKIE = open("cookies.txt","r")
    ARGS_COOKIE = FP_COOKIE.readline()
    FP_COOKIE.close()
    try:
        request = urllib2.Request(url);
        print '1'
        request.add_header('Cookie',ARGS_COOKIE)
        print '2'
        response = urllib2.urlopen(request)
        print '3'
        return response.read()
    except:
        print '[error]Fetch html fail'
        print url
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
    print url
    return  html[left:right]

def GetAllWeibo(uid):
    FP_COOKIE = open("cookies.txt","r")
    ARGS_COOKIE = FP_COOKIE.readline()
    FP_COOKIE.close()
    #each user, accountID is needed
    tmpUser = User()
    tmpUser.id = str(uid)
    tmpUser.domain = str(0)
    tmpUser.accountID = tmpUser.domain + tmpUser.id

    if tmpUser.domain == "0":
        FOLLOW_INIT_PATH = "http://weibo.com/u/" + tmpUser.id
        rawcontents = fetchUrl(FOLLOW_INIT_PATH)
        print 'fetch done'
        tmpUser.accountID = GetAccountId(tmpUser.id);
        print 'accountID done'
        if(not tmpUser.accountID.isdigit()):
            # print tmpUser.accountID
            print 're problem'
            return (False,'re problem')
        tmpUser.domain = str(tmpUser.accountID)[0:6]
        if tmpUser.accountID == "0":
            print 'get accountID fail'
            return (False,'get accountID fail')

    eachUser = tmpUser
    # init PATH
    PATH_REAL = "http://weibo.com/p/aj/v6/mblog/mbloglist?id=" + eachUser.accountID + "&domain=" + eachUser.domain + "&page="
    allWeiboList = []
    #fetch 200 page in default
    failTimes = 0
    for page in range(1,20):

        request = urllib2.Request(PATH_REAL + str(page))
        request.add_header('Cookie',ARGS_COOKIE)
        try:
            response = urllib2.urlopen(request)
            rawcontents = response.read()
        except:
            return (False,'url read error')
        tmpList = getWeiboList(rawcontents, eachUser.id)
        if len(tmpList) == 0:
            failTimes = failTimes + 1
            if failTimes >= 3:
                break
        else:
            allWeiboList.extend(tmpList)
    return (True,allWeiboList)

def svm_predict(allMsg):
    #connect db
    db = MySQLdb.connect(host="localhost", user="ljc", passwd="1", db="xinan")
    cursor = db.cursor()
    cursor.execute('set names "utf8"')
    # read v
    v = []

    #get data
    cursor.execute("select wid,word from evil_word limit 0,1000")
    allWord = cursor.fetchall()
    for eachWord in allWord:
        v.append(str(eachWord[1]))

    vLen = len(v)

    #load model
    clf = joblib.load('data/svm_m.dat')

    total = 0
    x = [0 for i in range(0, vLen)]
    for eachMsg in allMsg:
        #print eachMsg[1]
        soup = BeautifulSoup(str(eachMsg[1]))
        plaintext = soup.get_text().strip()
        seg_list = pseg.cut(plaintext)
        # x 为词库长度大小的词频列表 初始为 0
        for w in seg_list:
            #tmp_word 为分词结果
            tmp_word = w.word.strip()
            tmp_flag = w.flag[0]
            if len(tmp_word) == 0 or tmp_flag != 'n':
                continue
            else:
                total += 1
                if tmp_word not in v:
                    continue
                else:
                    x[v.index(tmp_word)] += 1
    x = [rate*1.0/total for rate in x]
    #使用之前的模型进行学习
    new_class =  clf.predict(x)
    return new_class[0]

if __name__ == '__main__':
    (flag,res) = GetAllWeibo('3796067394')
    exit(0)


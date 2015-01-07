# -*- coding:utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb
import chardet
from bs4 import BeautifulSoup
import jieba.posseg as pseg

#connect db
db = MySQLdb.connect(host="localhost", user="ljc", passwd="1", db="xinan")
cursor = db.cursor()
cursor.execute('set names "utf8"')


#取所有恶意用户
cursor.execute('select user_id from users where is_evil = 1')
allUser = cursor.fetchall()

#记录所有词
v = dict([])
word = []

for eachUser in allUser:
    cursor.execute('select content from post where user_id = %s',[str(eachUser[0])])
    allMsg = cursor.fetchall()
    for eachMsg in allMsg:
        #创建 beautifulsoup 对象
        soup = BeautifulSoup(str(eachMsg[0]))
        #获得 html 的文本并过滤空字符
        plaintext = soup.get_text().strip()
        #分词并标注词性
        seg_list = pseg.cut(plaintext)
        #对分词结果进行处理
        for w in seg_list:
            #词
            tmp_word = w.word.strip()
            #词性
            tmp_flag = w.flag[0]
            #只统计名词
            if len(tmp_word) == 0 or tmp_flag != 'n':
                continue
            else:
                if tmp_word not in word:
                    word.append(tmp_word)
                    v[word.index(tmp_word)] = 0
                v[word.index(tmp_word)] += 1

#根据词频排序
v = sorted(v.iteritems(),key = lambda d:d[1],reverse = True)

#tf 最高的 1000 个词作为训练特征
i = 0
for item in v:
    if i == 1000:
        break
    tmp_word = word[item[0]]
    tmp_word = tmp_word.encode('utf-8')
    cursor.execute('insert into word values(null,%s)',[tmp_word])
    db.commit()
    i += 1

#close db
cursor.close()
db.close()

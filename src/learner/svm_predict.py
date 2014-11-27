# -*- coding:utf-8 -*-
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

print 'connecting db...'
#connect db
db = MySQLdb.connect(host="localhost", user="ljc", passwd="1", db="xinan")
cursor = db.cursor()
cursor.execute('set names "utf8"')

# read v
v = []
print 'loading vocabulary...'
#get data
cursor.execute("select wid,word from evil_word")
allWord = cursor.fetchall()
for eachWord in allWord:
    v.append(str(eachWord[1]))

vLen = len(v)

#load model
print 'load model...'
clf = joblib.load('data/svm_m.dat')

while 1:
    print 'loading  row data...'
    #get data, 500 per time
    cursor.execute("select user_id from users where is_evil=0 limit 0,500")
    allUser = cursor.fetchall()
    if len(allUser) == 0:
        break
    for eachUser in allUser:
        cursor.execute('select content from post where user_id = %s',[eachUser[0]])
        allMsg = cursor.fetchall()
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
        #打印文本对应的分类
        print str(eachMsg[0]) + ' : ' + new_class[0]
        #把结果更新到数据库
        cursor.execute("update users set is_evil=%s where user_id=%s", (str(new_class[0]), int(eachMsg[0])))
        db.commit()

#close db
cursor.close()
db.close()

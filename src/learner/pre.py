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

v = dict([])

#get data
cursor.execute("select wid,word from evil_word")
allWord = cursor.fetchall()
for eachWord in allWord:
    v[str(eachWord[0])] = str(eachWord[1])

cursor.execute('select user_id,is_evil from users where is_evil != 0')
allUser = cursor.fetchall()

allX = []
allY = []
allWordCount = []
i = 0
for eachUser in allUser:
    allX.append([])
    tmp_total = 0
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
                tmp_total += 1
                if tmp_word in v:
                    #添加该词到 allX 中，以位置记录
                    allX[i].append(v.index(tmp_word))
    #处理完一篇文章，i ++
    i += 1
    #allY 记录这篇文章的分类
    allY.append(str(eachUser[1]))
    allWordCount.append(tmp_total)

fileHandle = open('data/y.dat','w')
fileHandle.write('\n'.join(allY))
fileHandle.close()

#vlen 为所有词数
vLen = len(v)
del allMsg
del allUser
del allY
del v
del i

i = 0
#计算每个用户的 TF
for eachUser in allX:
	tmp = [0 for x in range(0, vLen)]
	for eachWord in eachUser:
		tmp[eachWord] += 1
	tmp = [x*1.0/(allWordCount[i]+1) for x in tmp]
	allX[i] = ' '.join(str(c) for c in tmp)
    #文章数++
	i += 1


#打开文件
fileHandle = open('data/x.dat','w')
#写入文件
fileHandle.write('\n'.join(allX))
fileHandle.close()

db.commit()
#close db
cursor.close()
db.close()

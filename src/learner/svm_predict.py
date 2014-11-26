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

# read v
v = []
print 'loading vocabulary...'
#打开词库
f = open("data/v.dat")
#读取词库的每一行
line = f.readline()
i = 0
while line:
    #每个词加到 v 列表中
	v.append(str(line).strip())
    #下一行
	line = f.readline()
f.close()
#词库长度
vLen = len(v)

print 'connecting db...'
#connect db
#连接本地数据库
db = MySQLdb.connect(host="localhost", user="root", passwd="weloveutips8008", db="crawler")
cursor = db.cursor()
cursor.execute('set names "utf8"')

#load model
print 'load model...'
#读取训练模型
clf = joblib.load('data/svm_m.dat')

while 1:
	print 'loading  row data...'
	#get data, 500 per time
    #选择未分类的数据
	cursor.execute("select text_id,content from all_text where auto_class=0 limit 0,500")
	db.commit()
	allMsg = cursor.fetchall()
    #判断是否为空
	if len(allMsg) == 0:
		break
	for eachMsg in allMsg:
		#print eachMsg[1]
        #创建 beautifulsoup 对象
		soup = BeautifulSoup(str(eachMsg[1]))
        #获得 html 的文本并过滤空字符
		plaintext = soup.get_text().strip() 
        #分词并标注词性
		seg_list = pseg.cut(plaintext)
        # x 为词库长度大小的词频列表 初始为 0
		x = [0 for i in range(0, vLen)]
		for w in seg_list:
            #tmp_word 为分词结果
			tmp_word = w.word.strip()
            #只统计词库中出现过的词频
			if tmp_word not in v:
				continue
			else:
				x[v.index(tmp_word)] += 1
        #使用之前的模型进行学习
		new_class =  clf.predict(x)
        #打印文本对应的分类
		print str(eachMsg[0]) + ' : ' + new_class[0]
        #把结果更新到数据库
		cursor.execute("update all_text set auto_class=%s where text_id=%s", (str(new_class[0]), int(eachMsg[0])))
	db.commit()

#close db
cursor.close()
db.close()

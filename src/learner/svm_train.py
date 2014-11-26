# -*- coding:utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import chardet
from sklearn import svm
from sklearn.externals import joblib

x = []
y = []

# read x
f = open("data/x.dat")
line = f.readline()
i = 0
while line:
	tmp = line.split(' ')
	x.append(tmp)
	line = f.readline()
f.close()
# read y
f = open("data/y.dat")
line = f.readline()
while line:
	y.append(line.strip())
	line = f.readline()
f.close()

#train
clf = svm.SVC(gamma=0.001, C=100.)
print clf.fit(x[:100], y[:100])
#joblib.dump(clf, 'data/svm_m.dat')
print clf.score(x[100:], y[100:])

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

normal = 0
evil = 0

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
    tmp = line.strip()
    y.append(tmp)
    if tmp == '2':
        normal += 1
    else:
        evil += 1
    line = f.readline()
f.close()

print 'evil:'+str(evil)
print 'normal:'+str(normal)

#train
clf = svm.SVC(gamma=0.001, C=100.)
print clf.fit(x[:1000], y[:1000])
joblib.dump(clf, 'data/svm_m.dat')
#print clf.score(x[250:], y[250:])

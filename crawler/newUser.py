#!/usr/bin/env python
# encoding: utf-8


def CrawlPostForUser(u_id):


def CrawlFansForUser(u_id):
    pass

class UrlAnalyseError(Exception):
    def __init__(self, arg):
        self.args = arg

def getUidByUrl(url):
    uid = ''
    left = url.find('/u/') + len('/u/')
    right = len(url)
    while left < right and  url[left] >= '0' and url[left] <= '9':
        uid += url[left]
        left += 1
    try:
        if uid == '':
            raise UrlAnalyseError(('UrlAnalyseError', 'url analyse error'))
    except UrlAnalyseError, e:
        print e.args
        exit(1)
    return uid

if __name__ == '__main__':
    getUidByUrl('http://weibo.com/u/12312312312')

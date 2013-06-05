#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
从Hosts获取hosts文件写入系统
'''

import urllib2
import os
import re
import getSource
import time

hostsPath = r'/etc/hosts'

def getUpdate():
    print u'获取HostX数据'
    return getSource.getSource('https://github.com/orzTech/HostsX/raw/master/hosts', proxy='127.0.0.1:8087').decode('gbk').encode('utf-8')
    #urllib2.urlopen('http://hostsx.googlecode.com/svn/trunk/HostsX.orzhosts').read()

def getUpdateList():
    updateList = []
    with open('updateList.txt', 'r') as sfile:
        for line in sfile:
            updateList.append(line.strip())
    return updateList

def getCustom():
    custom = u'\n### 用户自定义项\n'.encode('utf-8')
    custom += open('custom.txt', 'r').read().encode('utf-8')
    return custom

def dataFilter(data, list):
    print u'写入HostX数据'
    sfile = open(hostsPath, 'w')
    splitData = re.split('^(@.+)$', data, flags=re.M)
    for i in range(1, len(splitData), 2):
        if True: #(splitData[i].strip() in list):
            sfile.write('###'+splitData[i].strip()+'\n')
            for line in splitData[i+1].split('\n'):
                sfile.write(line.strip()+'\n')
    sfile.write(getCustom())
    sfile.close()

def main():
    if os.path.isfile(hostsPath):
        os.remove(hostsPath)
    data = getUpdate()
    open('try.txt', 'w').write(data)
    list = getUpdateList()
    dataFilter(data, list)
    print u'写入HostX数据完成'
    time.sleep(2)

if __name__=='__main__':
    main()

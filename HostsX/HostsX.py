#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
从Hosts获取hosts文件写入系统
'''

import os
import re
import requests
import time

hostsPath = r'/etc/hosts'
url = 'http://hostsx.googlecode.com/svn/trunk/hosts'
http_proxy  = '127.0.0.1:8087'

def getDate():
    r = requests.get(url)
    return str(r.text)

def getCustom():
    custom = u'\n### user custom\n'
    custom += open('custom.txt', 'r').read()
    return custom

def dataFilter(data, list):
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
    os.chdir(os.path.dirname(__file__))
    print('获取HostX数据')
    data = getDate()
    #open('try.txt', 'w').write(data)
    print(u'写入HostX数据')
    dataFilter(data, list)
    print(u'写入HostX数据完成')
    time.sleep(2)

if __name__=='__main__':
    main()

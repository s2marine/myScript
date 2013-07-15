#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
'''
从集美大学教务处在线获取课表生成为ics日历文件
'''

import requests
from bs4 import BeautifulSoup
import datetime
import re

classTime = [600000, 80000, 100000, 140000, 160000, 190000]
weekFormat = [None, 'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

def getWeb(info):
    s = requests.session()
    r = s.get("http://cyjwgl.jmu.edu.cn/ViewSchedule/ViewClassSchedule.aspx")
    #open('t.html', 'w').write(r.content)
    soup = BeautifulSoup(r.content)
    inputList = soup.find_all('input')
    postData = {i.get('id'): i.get('value') or "" for i in inputList}
    #print postData
    postData["ctl00$ContentPlaceHolder1$SemesterSelect$semesterList"] = info['semester']
    postData["ctl00$ContentPlaceHolder1$ClassFilter$ClassText"] = info['class']
    postData["ctl00$ContentPlaceHolder1$ViewSchedule"] = "查询课表"
    r = s.post("http://cyjwgl.jmu.edu.cn/ViewSchedule/ViewClassSchedule.aspx", postData)
    #open('t.html', 'w').write(r.content)
    soup = BeautifulSoup(r.content)
    return soup.find('table', id="ctl00_ContentPlaceHolder3_ScheduleTable")

def analyzeWeb(table):
    strClass = []
    trs = table.find_all('tr')
    for whichClass in range(1, len(trs)):
        tds = trs[whichClass].find_all('td')
        for whichWeek in range(1, len(tds)):
            c = tds[whichWeek].contents[0].contents[0].strip()
            for c in c.split('★'):
                if c: 
                    strClass.append(' '.join((str(whichWeek), str(whichClass), c, )))
    #for i in strClass:
    #    print i
    return strClass

def analyzeClass(strClass, info):
    #1 1 思想道德修养与法律基础  诚毅8-301 陈丽云 1-15
    classDataList = []
    for eachClass in strClass:
        eachClass = eachClass
        eachClass = re.sub('\(.+?\)', '', eachClass)
        s = eachClass.split(' ')
        w = re.findall('\d+', s[6])
        startWeek = int(w[0])
        if len(w)==1:
            endWeek = int(w[0])
        else:
            endWeek = int(w[1])
        if (s[6].find('单')==-1 and s[6].find('双')==-1):
            interval = 1
        else:
            interval = 2
        startData = info['schoolStart']+datetime.timedelta(days=7*(startWeek-1)+int(s[0])-1)
        classData = {'className': s[2],
                     'week': weekFormat[int(s[0])],
                     'startTime': classTime[int(s[1])],
                     'endTime': classTime[int(s[1])]+20000,
                     'location': s[4],
                     'startData': startData,
                     'count': str(int(((endWeek-startWeek)/interval)+1)),
                     'interval': str(interval)
                    }
        classDataList.append(classData)
    return classDataList


def outputICS(classDataList, info):
    with open(info['class']+'.ics', 'w') as f:
        f.write("BEGIN:VCALENDAR\n")
        for eachEvent in classDataList:
            f.write("BEGIN:VEVENT\n")
            f.write("DTSTART;TZID=Asia/Shanghai:"
                    +eachEvent['startData'].strftime('%Y%m%d')+'T'
                    +'%06d' % eachEvent['startTime']+"\n")
            f.write("DTEND;TZID=Asia/Shanghai:"
                    +eachEvent['startData'].strftime('%Y%m%d')+'T'
                    +'%06d' % eachEvent['endTime']+"\n")
            f.write("RRULE:FREQ=WEEKLY;BYDAY="+eachEvent['week']+
                    ";COUNT="+eachEvent['count']+
                    ";INTERVAL="+eachEvent['interval']+"\n")
            f.write("DESCRIPTION:"+"\n")
            f.write("LOCATION:"+eachEvent['location']+"\n")
            f.write("SUMMARY:"+eachEvent['className']+"\n")
            f.write("END:VEVENT\n")
        f.write("END:VCALENDAR")


def main():
    schoolStart = datetime.date(*(2013, 9, 2))
    info = {'semester': 20131, 'class': '软件1292', 'schoolStart': schoolStart}
    table = getWeb(info)
    strClass = analyzeWeb(table)
    classDataList = analyzeClass(strClass, info)
    print(classDataList)
    outputICS(classDataList, info)

if __name__=='__main__':
    main()

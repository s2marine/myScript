# -*- encoding:utf-8 -*-
import sys
import logging
sys.path.append('./lib/')
sys.path.append('./RSS/')
import json
import datetime
import re
import webapp2
from google.appengine.ext import db
import requests
import PyRSS2Gen
from bs4 import BeautifulSoup
from RSSClass import *


class pageChengyiTimetable(webapp2.RequestHandler):
    def get(self):
        self.argsInit()
        o = RSSChengyiTimetable(self.urlArgs)
        o.getRSS()
        self.response.out.write(o.RSSOut)

    def argsInit(self):
        whatArgsNeed = ['class']
        self.urlArgs = {i:self.request.get(i) for i in whatArgsNeed}
        if not self.urlArgs['class']:
            self.abort(400, u'缺少class参数')

class RSSChengyiTimetable(RSSObject):
    def __init__(self, urlArgs):
        super(RSSChengyiTimetable, self).__init__('ChengyiTimetable', urlArgs, 60*60)
        self.MAXItems = 50

    def getWeb(self, info):
        s = requests.session()
        r = s.get("http://cyjwgl.jmu.edu.cn/ViewSchedule/ViewClassSchedule.aspx")
        #open('t.html', 'w').write(r.content)
        soup = BeautifulSoup(r.content)
        inputList = soup.find_all('input')
        postData = {i.get('id'): i.get('value') or "" for i in inputList}
        #print postData
        postData["ctl00$ContentPlaceHolder1$SemesterSelect$semesterList"] = info['semester']
        postData["ctl00$ContentPlaceHolder1$ClassFilter$ClassText"] = info['class']
        postData["ctl00$ContentPlaceHolder1$ViewSchedule"] = u"查询课表"
        r = s.post("http://cyjwgl.jmu.edu.cn/ViewSchedule/ViewClassSchedule.aspx", postData)
        #open('t.html', 'w').write(r.content)
        soup = BeautifulSoup(r.content)
        return soup.find('table', id="ctl00_ContentPlaceHolder3_ScheduleTable")

    def analyzeWeb(self, table):
        strClass = []
        #print table
        trs = table.find_all('tr')
        for whichClass in range(1, len(trs)):
            tds = trs[whichClass].find_all('td')
            for whichWeek in range(1, len(tds)):
                c = tds[whichWeek].contents[0].contents[0].strip()
                for c in c.split(u'★'):
                    if c:
                        strClass.append(' '.join((str(whichWeek), str(whichClass), c, )))
        #for i in strClass:
        #    print i
        return strClass


    def getRSSDataFromWeb(self):
        now = datetime.datetime.now()
        semester = str(now.year)
        if 2<now.month<8:
            semester += '2'
        else:
            semester += '1'
        info = {'semester': semester,
                'class': self.urlArgs['class']}
        table = self.getWeb(info)
        strClass = self.analyzeWeb(table)

        self.RSSData['title'] = u'诚毅'+self.urlArgs['class']+u'课程表'
        self.RSSData['link'] = 'http://cyrj.tk/cal/'
        self.RSSData['description'] = u'订阅追踪教务处课表信息'
        if (self.RSSData['title']!=self.RSSInfo.title or
                self.RSSData['link']!=self.RSSInfo.link or
                self.RSSData['description']!=self.RSSInfo.description):
            self.RSSInfo.title = self.RSSData['title']
            self.RSSInfo.link = self.RSSData['link']
            self.RSSInfo.description = self.RSSData['description']
            self.db['put'].append(self.RSSInfo)

        oldClass = [i.description for i in self.RSSDatas]
        difference = list(set(oldClass).difference(set(strClass)) | set(strClass).difference(set(oldClass)))
        items = self.RSSData['items'] = []
        times = 0
        for i in difference:
            self.isNew = True
            if i in oldClass:
                title = 'del: '
            elif i in strClass:
                title = 'add: '
            title += i
            link = 'https://'+os.environ.get('HTTP_HOST')+'/RSS/'+self.RSSName+'?'+self.strUrlArgs
            description = i
            guid = i
            pubDate = datetime.datetime.now()
            #pubDate -= datetime.timedelta(hours=8)
            items.append({
                'title':title,
                'link':link,
                'description':description,
                'guid':guid,
                'pubDate':pubDate})
            self.db['put'].append(DBRSSData(
                RSSName = self.RSSName,
                strUrlArgs = self.strUrlArgs,
                title = title,
                link = link,
                description = description,
                guid = guid,
                pubDate = pubDate))
            logging.info("%s: %s" % (self.RSSName, title))
            times += 1
            if times>=self.MAXItems:
                break
        if len(self.RSSDatas)+times>self.MAXItems:
            self.db['del'] += self.RSSDatas[self.MAXItems-len(self.RSSDatas)-times:]

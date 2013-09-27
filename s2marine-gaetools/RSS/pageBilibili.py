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

class pageBilibili(webapp2.RequestHandler):
    def get(self):
        o = RSSBilibili(self, {})
        o.getRSS()
        self.response.out.write(o.RSSOut)

class RSSBilibili(RSSObject):
    def __init__(self, handler, urlArgs):
        super(RSSBilibili, self).__init__(handler, 'Bilibili', urlArgs, [23*3600])
        self.MAXItems = 20

    def getRSSDataFromWeb(self):
        url = 'http://www.bilibili.tv/index/ranking.json'
        r = requests.get(url)
        src = r.content
        r.close()
        datas = json.loads(src)['hot']['list']

        self.RSSData['title'] = 'Bilibili'
        self.RSSData['link'] = 'http://www.bilibili.tv/'
        self.RSSData['description'] = u'嗶哩嗶哩 - ( ゜- ゜)つロ 乾杯~ - bilibili.tv'

        if (self.RSSData['title']!=self.RSSInfo.title or
                self.RSSData['link']!=self.RSSInfo.link or
                self.RSSData['description']!=self.RSSInfo.description):
            self.RSSInfo.title = self.RSSData['title']
            self.RSSInfo.link = self.RSSData['link']
            self.RSSInfo.description = self.RSSData['description']
            self.db['put'].append(self.RSSInfo)

        oldGuids = [i.guid for i in self.RSSDatas]
        items = self.RSSData['items'] = []
        times = 0
        sumTimes = 0
        for i, data in datas.iteritems():
            title = data['title']
            link = 'http://www.bilibili.tv/video/av'+str(data['aid'])+'/'
            description = '<img src="'+data['pic']+'"/>'
            guid = link
            pubDate = datetime.datetime.strptime(data['create'], '%Y-%m-%d %H:%M')
            pubDate -= datetime.timedelta(hours=8)
            items.append({
                'title':title,
                'link':link,
                'description':description,
                'guid':guid,
                'pubDate':pubDate})
            if not guid in oldGuids:
                self.isNew = True
                self.db['put'].append(DBRSSData(
                    RSSName = self.RSSName,
                    strUrlArgs = self.strUrlArgs,
                    title = title,
                    link = link,
                    description = description,
                    guid = guid,
                    pubDate = pubDate))
                logging.info("%s: add %s" % (self.RSSName, title))
                times += 1
            sumTimes += 1
            if times>=self.MAXItems:
                break
            if sumTimes>=self.MAXItems:
                break
        if len(self.RSSDatas)+times>self.MAXItems:
            self.db['del'] += self.RSSDatas[self.MAXItems-len(self.RSSDatas)-times:]


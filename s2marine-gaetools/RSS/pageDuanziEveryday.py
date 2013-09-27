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

class pageDuanziEveryday(webapp2.RequestHandler):
    def get(self):
        o = RSSDuanziEveryday(self, {})
        o.getRSS()
        self.response.out.write(o.RSSOut)

class RSSDuanziEveryday(RSSObject):
    def __init__(self, handler, urlArgs):
        super(RSSDuanziEveryday, self).__init__(handler, 'DuanziEveryday', urlArgs, 
                [(21-8)*3600, (22-8)*3600, (23-8)*3600, (24-8)*3600])
        self.key = 'AIzaSyBJid1_6Art9j5bKy37XeopNxXjn3pWk08'
        self.people = '114955851650599222028'
        self.filterText = u'.*?段子荟萃.*\d+-\d+'
        self.MAXItems = 10

    def getRSSDataFromWeb(self):
        apiUrl = 'https://www.googleapis.com/plus/v1/people/'+self.people+'/activities/public?maxResults=50&key='+self.key
        r = requests.get(apiUrl)
        src = r.content
        r.close()
        p = re.compile(self.filterText)
        reJson = json.loads(src)
        oldGuids = [i.guid for i in self.RSSDatas]
        items = self.RSSData['items'] = []
        times = 0
        sumTimes = 0
        format = '%Y-%m-%dT%H:%M:%S.%fZ'
        for eachItem in reJson['items']:
            title = eachItem['title']
            tryFindTitle = p.search(title)
            if tryFindTitle:
                title = tryFindTitle.group()
                link = eachItem['url']
                description = eachItem['object']['content']
                guid = link
                pubDate = datetime.datetime.strptime(eachItem['updated'], format)
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
                    times += 1
                    logging.info("%s: add %s" % (self.RSSName, title))
                sumTimes += 1
                if times>=self.MAXItems:
                    break
                if sumTimes>=self.MAXItems:
                    break
        if len(self.RSSDatas)+times>self.MAXItems:
            self.db['del'] += self.RSSDatas[self.MAXItems-len(self.RSSDatas)-times:]

        self.RSSData['title'] =  u'一日段子荟萃'
        self.RSSData['link'] = 'https://plus.google.com/114955851650599222028'
        self.RSSData['description'] = u'一日段子荟萃'
        if (self.RSSData['title']!=self.RSSInfo.title or
                self.RSSData['link']!=self.RSSInfo.link or
                self.RSSData['description']!=self.RSSInfo.description):
            self.RSSInfo.title = self.RSSData['title']
            self.RSSInfo.link = self.RSSData['link']
            self.RSSInfo.description = self.RSSData['description']
            self.db['put'].append(self.RSSInfo)

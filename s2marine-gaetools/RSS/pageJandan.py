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

class pageJandan(webapp2.RequestHandler):
    def get(self):
        o = RSSJandan(self, {})
        o.getRSS()
        self.response.out.write(o.RSSOut)

class RSSJandan(RSSObject):
    def __init__(self, handler, urlArgs):
        super(RSSJandan, self).__init__(handler, 'Jandan', urlArgs, [7200])
        self.MAXItems = 20

    def getRSSDataFromWeb(self):
        url = 'http://jandan.net'
        r = requests.get(url)
        src = r.content
        r.close()
        authors = BeautifulSoup(src).findAll('div', attrs={"class":"acv_author"})

        self.RSSData['title'] = u'煎蛋24小时最佳评论'
        self.RSSData['link'] = 'http://www.jandan.net/'
        self.RSSData['description'] = u'煎蛋24小时最佳评论'

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
        for author in authors:
            title = author.text #.encode('utf-8')
            link = author.find('a').get('href')
            voteId = author.findNext('div', attrs={"class":"vote votehot"}).get("id")
            comment = author.findNext('div', attrs={"class":"acv_comment"})
            for i in comment.findAll('img'):
                i.insert_before(BeautifulSoup("<br/>"))
                i.insert_after(BeautifulSoup("<br/>"))
            description = comment.prettify()
            guid = voteId
            pubDate = datetime.datetime.now()
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


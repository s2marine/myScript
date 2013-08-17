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

class pageChengyi(webapp2.RequestHandler):
    def get(self):
        o = RSSChengyi({})
        o.getRSS()
        self.response.out.write(o.RSSOut)

class RSSChengyi(RSSObject):
    def __init__(self, urlArgs):
        super(RSSChengyi, self).__init__('Chengyi', urlArgs, 3600)
        self.MAXItems = 20

    def getRSSDataFromWeb(self):
        self.RSSData['title'] = u'诚毅通知集合'
        self.RSSData['link'] = 'http://cyrj.tk'
        self.RSSData['description'] = u'诚毅学院各个网站通知集合'

        if (self.RSSData['title']!=self.RSSInfo.title or
                self.RSSData['link']!=self.RSSInfo.link or
                self.RSSData['description']!=self.RSSInfo.description):
            self.RSSInfo.title = self.RSSData['title']
            self.RSSInfo.link = self.RSSData['link']
            self.RSSInfo.description = self.RSSData['description']
            self.db['put'].append(self.RSSInfo)

        oldGuids = [i.guid for i in self.RSSDatas]

        waitList = []

        #教务部
        url = u'http://cyjwb.jmu.edu.cn/lists.asp?lbm=%CD%A8%D6%AA%B9%AB%B8%E6'
        r = requests.get(url)
        src = r.content
        r.close()
        soup = BeautifulSoup(src)
        table = soup.findAll('table')[2]
        p = re.compile(u'\d+-\d+-\d+ \d+:\d+:\d+')
        for i in table.findAll('a')[:-3]: #去掉最后的翻页
            title = i.text.strip()
            link = 'http://cyjwb.jmu.edu.cn/'+i.get('href')
            description = ''
            guid = link
            if guid in oldGuids:
                break
            pubDateStr = p.search(i.next_sibling.next_sibling.text).group()
            pubDate = datetime.datetime.strptime(pubDateStr, '%Y-%m-%d %H:%M:%S')
            waitList.append({
                'title':title,
                'link':link,
                'description':description,
                'guid':guid,
                'pubDate':pubDate})
        

        #诚毅学院
        url = u'http://chengyi.jmu.edu.cn/NewsList.aspx?level=2&type=通知通告'
        r = requests.get(url)
        src = r.content
        r.close()
        soup = BeautifulSoup(src)
        table = soup.find('div', attrs={'id':'div_con'}).find('table')
        p = re.compile(u'\d+年\d+月\d+日')
        for tr in table.findAll('tr'):
            tds = tr.findAll('td')
            if len(tds)!=3:
                continue
            title = tds[1].text.strip()
            link = 'http://chengyi.jmu.edu.cn/'+tds[1].a.get('href')
            description = ''
            guid = link
            if guid in oldGuids:
                break
            pubDateStr = p.search(tds[2].text).group()
            pubDate = datetime.datetime.strptime(pubDateStr.encode('utf-8'), '%Y年%m月%d日')
            waitList.append({
                'title':title,
                'link':link,
                'description':description,
                'guid':guid,
                'pubDate':pubDate})


        #体育教研部
        url = u'http://cytyjys.jmu.edu.cn/Info/?id=2'
        r = requests.get(url)
        src = r.content
        r.close()
        soup = BeautifulSoup(src)
        div = soup.find('div', attrs={'class':'m10'})
        titles = [i.find('a') for i in div.findAll('h1', attrs={'class':'list_title'})]
        links = [i.get('href') for i in titles]
        titles = [i.text for i in titles]
        pubDateStrs = [i.findAll('span')[2].text for i in div.findAll('div', attrs={'class':'list_other'})]
        for i in range(0, len(titles)):
            title = titles[i]
            link = 'http://cytyjys.jmu.edu.cn/'+links[i]
            description = ''
            guid = link
            if guid in oldGuids:
                break
            pubDate = datetime.datetime.strptime(pubDateStrs[i], '%Y-%m-%d %H.%M.%S')
            waitList.append({
                'title':title,
                'link':link,
                'description':description,
                'guid':guid,
                'pubDate':pubDate})

        items = self.RSSData['items'] = []
        times = 0
        sumTimes = 0
        for i in sorted(waitList, key=lambda x:x['pubDate'])[::-1]:
            title = i['title']
            link = i['link']
            description = i['description']
            guid = i['guid']
            pubDate = i['pubDate']
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


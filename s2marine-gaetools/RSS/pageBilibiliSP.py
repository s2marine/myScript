# -*- encoding:utf-8 -*-
import sys
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

class pageBilibiliSP(webapp2.RequestHandler):
    def get(self):
        self.argsInit()
        o = RSSBilibiliSP(self.urlArgs)
        o.getRSS()
        self.response.out.write(o.RSSOut)

    def argsInit(self):
        whatArgsNeed = ['url', 'season_id']
        self.urlArgs = {i:self.request.get(i) for i in whatArgsNeed}
        if not self.urlArgs['url']:
            self.abort(400, u'缺少url参数')
        if "http://www.bilibili.tv/sppage/" in self.urlArgs['url']:
            self.abort(410, u'旧的请求方法已经失效了')

class RSSBilibiliSP(RSSObject):
    def __init__(self, urlArgs):
        super(RSSBilibiliSP, self).__init__('BilibiliSP', urlArgs, 2*60*60)
        self.MAXItems = 10

    def getRSSDataFromWeb(self):
        url = self.urlArgs['url']
        r = requests.get(url)
        src = r.content
        r.close()
        spid = re.search('var spid ?= ?"(\d+?)"', src).group(1)
        isbangumi = re.search('var isbangumi ?= ?"(\d+?)"', src).group(1)
        soup = BeautifulSoup(src)
        title = soup.find('h1').text
        description = soup.find('p', attrs={'id':'info-desc'}).text
        seasonIds = [] if isbangumi=='0' else [i['season_id'] for i in soup.find(attrs={'id':'season_selector'}).findAll('li')]
        
        if isbangumi=='0':
            addNewUrl = 'http://www.bilibili.tv/sppage/ad-new-'+spid
        elif isbangumi=='1':
            addNewUrl = 'http://www.bilibili.tv/sppage/bangumi-'+spid
        if self.urlArgs['season_id']:
            addNewUrl += '-'+self.urlArgs['season_id']
        elif seasonIds:
            addNewUrl += '-'+seasonIds[-1]
        addNewUrl += '-1.html'

        r = requests.get(addNewUrl)
        src = r.content
        r.close()
        soup = BeautifulSoup(src)

        self.RSSData['title'] = title
        self.RSSData['link'] = self.urlArgs['url']
        self.RSSData['description'] = description
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
        for i in soup.findAll('div', attrs={'class':'po'}):
            title = i.find('div', attrs={'class':'t'}).text
            link = 'http://www.bilibili.tv'+i.find('a').get('href')
            description = '<img src="'+i.find('img').get('src')+'"/>'
            guid = 'http://www.bilibili.tv'+i.find('a').get('href')
            pubDate = datetime.datetime.strptime(i.get('tg'), '%Y-%m-%d %H:%M')
            items.append({
                'title':title,
                'link':link,
                'description':description,
                'guid':guid,
                'pubDate':pubDate})
            if not guid in oldGuids:
                self.db['put'].append(DBRSSData(
                    RSSName = self.RSSName,
                    strUrlArgs = self.strUrlArgs,
                    title = title,
                    link = link,
                    description = description,
                    guid = guid,
                    pubDate = pubDate))
                times += 1
            if times>=self.MAXItems:
                break
        if len(self.RSSDatas)+times>self.MAXItems:
            self.db['del'] += self.RSSDatas[self.MAXItems-len(self.RSSDatas)-times:]


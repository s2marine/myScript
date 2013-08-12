# -*- encoding:utf-8 -*-
import sys
import os
import urllib
import logging
sys.path.append('./lib/')
from google.appengine.ext import db
from google.appengine.api import urlfetch
import json
import datetime
import PyRSS2Gen
#from bs4 import BeautifulSoup

class MyRSS2(PyRSS2Gen.RSS2):
    def publish_extensions(self, handler, outfile):
        outfile.write('<atom:link rel="hub" href="https://pubsubhubbub.appspot.com/" />')

class DBRSSCron(db.Model):
    RSSName = db.StringProperty()
    strUrlArgs = db.StringProperty()
    updateInterval = db.StringProperty()
    nextUpdateTime = db.DateTimeProperty()

    def setTimeNow(self):
        self.nextUpdateTime = datetime.datetime.now()

    def setNextTime(self):
        if not self.nextUpdateTime:
            self.setTimeNow()
            return
        updateInterval = json.loads(self.updateInterval)
        if type(updateInterval) is int:
            self.nextUpdateTime += datetime.timedelta(seconds=updateInterval-600)
        elif type(updateInterval) is list:
            today = datetime.date.today()
            todayTime = datetime.datetime.combine(today, datetime.time())
            now = datetime.datetime.now()
            for i in updateInterval:
                time = datetime.timedelta(seconds=i)
                if todayTime+time >= now:
                    self.nextUpdateTime = todayTime+time
                    return 
            nextDay = todayTime+datetime.timedelta(days=1)
            self.nextUpdateTime = nextDay+datetime.timedelta(seconds=updateInterval[0])

    def isTime(self):
        now = datetime.datetime.now()
        return now >= self.nextUpdateTime

    def getUrlArgs(self):
        return json.loads(self.strUrlArgs)

    def setStrUrlArgs(self, urlArgs):
        self.strUrlArgs = json.dumps(urlArgs, sort_keys=True)




class DBRSSInfo(db.Model):
    RSSName = db.StringProperty()
    strUrlArgs = db.StringProperty()
    title = db.StringProperty()
    link = db.StringProperty()
    description = db.TextProperty()

class DBRSSData(db.Model):
    RSSName = db.StringProperty()
    strUrlArgs = db.StringProperty()
    title = db.StringProperty()
    link = db.StringProperty()
    description = db.TextProperty()
    guid = db.StringProperty()
    pubDate = db.DateTimeProperty()

class RSSObject(object):
    '''
    self.RSSName
    self.strUrlArgs
    self.urlArgs
    self.updateInterval


    '''




    def __init__(self, RSSName, urlArgs, updateInterval):
        self.RSSName = RSSName
        self.urlArgs = urlArgs
        self.strUrlArgs = json.dumps(self.urlArgs, sort_keys=True)
        self.updateInterval = updateInterval
        self.RSSData = {}
        self.db = {'put':[], 'del':[]}

    def getRSS(self):
        self.checkDB()
        self.initDB()
        if self.isInDB:
            self.getRSSDataFromDB()
        else:
            self.getRSSDataFromWeb()
            self.updateNextTime()
            self.saveDB()
        self.setRSSOut()

    def checkDB(self):
        RSSInfos = db.GqlQuery('SELECT * FROM DBRSSInfo WHERE \
                RSSName=:1 AND strUrlArgs=:2', 
                self.RSSName,
                self.strUrlArgs).fetch(None)
        if RSSInfos:
            self.isInDB = True
            self.RSSInfo = RSSInfos[0]
        else:
            self.isInDB = False

    def initDB(self):
        if self.isInDB:
            self.RSSDatas = db.GqlQuery('SELECT * FROM DBRSSData WHERE \
                    RSSName=:1 AND strUrlArgs=:2 ORDER BY pubDate DESC', 
                    self.RSSName,
                    self.strUrlArgs).fetch(None)
        else:
            self.RSSCron = DBRSSCron(
                    RSSName = self.RSSName,
                    strUrlArgs = self.strUrlArgs,
                    updateInterval = json.dumps(self.updateInterval),
                    nextUpdateTime = datetime.datetime.now())
            self.RSSInfo = DBRSSInfo(
                    RSSName = self.RSSName,
                    strUrlArgs = self.strUrlArgs)
            self.RSSDatas = []




    def getRSSDataFromDB(self):
        self.RSSData['title'] = self.RSSInfo.title
        self.RSSData['link'] = self.RSSInfo.link
        self.RSSData['description'] = self.RSSInfo.description
        self.RSSData['items'] = []

        for data in self.RSSDatas:
            self.RSSData['items'].append({
                'title':data.title,
                'link':data.link,
                'description':data.description,
                'guid':data.guid,
                'pubDate':data.pubDate})

    def setRSSOut(self):
        rss = MyRSS2(
                title = self.RSSData['title'], 
                link = self.RSSData['link'], 
                description = self.RSSData['description'],
                items = []
                ) 
        for item in self.RSSData['items']:
            rss.items.append(PyRSS2Gen.RSSItem(
                title = item['title'], 
                link = item['link'], 
                description = item['description'],
                guid = item['guid'], 
                pubDate = item['pubDate']))

        self.RSSOut = rss.to_xml('utf-8')
        #soup = BeautifulSoup(rss.to_xml('utf-8'))
        #self.RSSOut = soup.prettify()


    def getRSSDataFromWeb(self):
        pass

    def saveDB(self):
        db.put(self.db['put'])
        db.delete(self.db['del'])

    def cronUpdate(self, RSSCron):
        self.RSSCron = RSSCron
        self.checkDB()
        self.initDB()
        print '\n'*10
        if self.RSSCron.nextUpdateTime<=datetime.datetime.now():
            self.getRSSDataFromWeb()
            self.updateNextTime()
            self.saveDB()
            self.pushToPubsubhubbub()

    def updateNextTime(self):
        self.RSSCron.setNextTime()
        self.db['put'].append(self.RSSCron)

    def pushToPubsubhubbub(self):
        hub_url = 'https://pubsubhubbub.appspot.com/'
        strUrlArgs = '&'.join([(j+'='+k).encode('utf-8') for j,k in self.urlArgs.items() if k])
        hubUrl = 'https://'+os.environ.get('HTTP_HOST')+'/RSS/'+self.RSSName+'?'+strUrlArgs
        data = urllib.urlencode({
            'hub.url': hubUrl,
            'hub.mode': 'publish'})
        response = urlfetch.fetch(hub_url, data, urlfetch.POST)
        logging.info("%s code is %d" % (self.RSSName, response.status_code))

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
        self.links = links = {}
        for author in authors:
            title = author.text
            voteId = int(self.getVoteIdFromMain(author.findNext('div', attrs={"class":"vote votehot"}).get("id")))
            link = author.find('a').get('href')
            if link=="http://jandan.net/pic":
                link = self.getLink(voteId)
            comment = author.findNext('div', attrs={"class":"acv_comment"})
            for i in comment.findAll('img'):
                i.insert_before(BeautifulSoup("<br/>"))
                i.insert_after(BeautifulSoup("<br/>"))
            description = comment.prettify()
            guid = link
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

    def getVoteIdFromMain(self, string):
        return int(re.search('(?<=-2)\d+$', string).group())

    def getVoteIdNormal(self, string):
        return int(re.search('(?<=-)\d+$', string).group())

    def getPageNum(self, string):
        return int(re.search('(?<=page-)\d+', string).group())

    def getLink(self, voteId):
        if voteId in self.links:
            return self.links[voteId]
        elif self.links and (voteId>min(self.links.keys()) or len(self.links)>100):
            return "http://jandan.net/pic"
        else:
            self.getLinksFromPage()
            return self.getLink(voteId)

    def getLinksFromPage(self):
        if self.links=={}:
            url = "http://jandan.net/pic"
        else:
            minLink = self.links[min(self.links.keys())]
            url = "http://jandan.net/pic/page-"+str(self.getPageNum(minLink)-1)
        self.getPageLink(url)

    def getPageLink(self, page):
        r = requests.get(page)
        src = r.content
        r.close()
        righttexts = BeautifulSoup(src).findAll('span', attrs={'class':'righttext'})
        for righttext in righttexts:
            a = righttext.find('a')
            link = a['href']
            self.links[int(self.getVoteIdNormal(link))] = link

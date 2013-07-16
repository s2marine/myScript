#coding:utf-8
import webapp2
import PyRSS2Gen
import json
import urllib2
import HTMLParser
import re

class pageDuanziEveryday(webapp2.RequestHandler):
    key = 'AIzaSyBJid1_6Art9j5bKy37XeopNxXjn3pWk08'
    
    def get(self):
        self.people = self.request.get('people')
        if not self.people:
            self.response.out.write(u'缺少参数people')
            return
        self.filterText = self.request.get('filterText')
        if not self.filterText:
            self.filterText = ''
        self.maxResults = self.request.get('maxResults')
        if not self.maxResults:
            self.maxResults = 10
        rss = self.getRSS()
        self.response.out.write(rss)

    def getRSS(self):
        apiUrl = 'https://www.googleapis.com/plus/v1/people/'+self.people+'/activities/public?maxResults='+str(self.maxResults)+'&key='+self.key
        src = urllib2.urlopen(apiUrl).read()
        p = re.compile(self.filterText)
        reJson = json.loads(src)
        itemList = []
        for eachItem in reJson['items']:
            title = eachItem['title']
            tryFindTitle = p.search(title)
            if tryFindTitle:
                itemList.append(PyRSS2Gen.RSSItem(
                    title = tryFindTitle.group(), 
                    link = eachItem['url'], 
                    description = eachItem['object']['content']
                    ))
        rss = PyRSS2Gen.RSS2(
            title = u'一日段子荟萃',
            link ='https://plus.google.com/114955851650599222028',
            description = u'一日段子荟萃'
            )
        rss.items = itemList
        return rss.to_xml('utf-8')


#coding=utf-8
import webapp2
import PyRSS2Gen
import BeautifulSoup
import urllib2
import re

class pageBilibiliSP(webapp2.RequestHandler):
    def get(self):
        self.url = self.request.get('url')
        if not self.url:
            self.response.out.write(u'缺少url')
            return
        rss = self.getRSS()
        self.response.out.write(rss)

    def getRSS(self):
        src = urllib2.urlopen(self.url).read()
        spid = re.search('var spid ?= ?"(\d+?)"', src).group(1)
        isbangumi = re.search('var isbangumi ?= ?"(\d+?)"', src).group(1)
        soup = BeautifulSoup.BeautifulSoup(src)
        title = soup.find('h1').text
        description = soup.find('p', attrs={'id':'info-desc'}).text
        
        if isbangumi=='0':
            addNewUrl = 'http://www.bilibili.tv/sppage/ad-new-'+spid+'-1.html'
        elif isbangumi=='1':
            addNewUrl = 'http://www.bilibili.tv/sppage/bangumi-'+spid+'-1.html'
        src = urllib2.urlopen(addNewUrl).read()
        soup = BeautifulSoup.BeautifulSoup(src)

        tList = []
        for i in soup.findAll('div', attrs={'class':'po'}):
            titleadd = i.contents[1].contents[4]
            linkadd = r'http://www.bilibili.tv'+i.contents[1].get('href')
            descriptionadd = i.contents[1].contents[0]
            tList.append({'title':titleadd, 'link':linkadd, 'description':descriptionadd})

        itemList = []
        for i in tList:
            itemList.append(PyRSS2Gen.RSSItem(
                title = unicode(i['title'].text),
                link = i['link'],
                description = unicode(i['description'])
                ))

        rss = PyRSS2Gen.RSS2(
            title = title,
            link = self.url,
            description = description
            )
        rss.items = itemList
        return rss.to_xml('utf-8')

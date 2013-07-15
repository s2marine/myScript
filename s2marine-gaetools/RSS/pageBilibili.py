#coding=utf-8
import webapp2
from google.appengine.ext import db
import PyRSS2Gen
import BeautifulSoup
class pageBilibili(webapp2.RequestHandler):
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        rss = self.getDB()
        self.response.out.write(rss)
    def getDB(self):
        DBBILIBILIs = db.GqlQuery('SELECT * FROM DBBILIBILI ORDER BY date DESC')

        itemList = []
        for data in DBBILIBILIs:
            itemList.append(PyRSS2Gen.RSSItem(
                title = data.title,
                link = data.link,
                description = data.description
                ))

        rss = PyRSS2Gen.RSS2(
            title = 'bilibili',
            link = 'http://www.bilibili.tv/',
            description = u'嗶哩嗶哩 - ( ゜- ゜)つロ 乾杯~ - bilibili.tv'
            )
        rss.items = itemList
        return rss.to_xml('utf-8')

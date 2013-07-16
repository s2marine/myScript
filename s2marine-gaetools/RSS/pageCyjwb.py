#coding=utf-8
import webapp2
from google.appengine.ext import db
import PyRSS2Gen
import BeautifulSoup
class pageCyjwb(webapp2.RequestHandler):
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        rss = self.getDB()
        self.response.out.write(rss)
    def getDB(self):
        DBCyjwb = db.GqlQuery('SELECT * FROM DBCyjwb ORDER BY date DESC')

        itemList = []
        for data in DBCyjwb:
            itemList.append(PyRSS2Gen.RSSItem(
                title = unicode(data.title),
                link = data.link,
                description = data.description
                ))

        rss = PyRSS2Gen.RSS2(
            title = u'诚毅教务部',
            link = 'http://cyjwb.jmu.edu.cn/',
            description = u'集美大学诚毅学院教务部官方网站'
            )
        rss.items = itemList
        return rss.to_xml('utf-8')

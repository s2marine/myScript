#coding=utf-8
import webapp2
from google.appengine.ext import db
import PyRSS2Gen
import BeautifulSoup
class page3DM(webapp2.RequestHandler):
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        rss = self.getDB()
        self.response.out.write(rss)
    def getDB(self):
        DB3DMs = db.GqlQuery('SELECT * FROM DB3DM ORDER BY date DESC')

        itemList = []
        for data in DB3DMs:
            itemList.append(PyRSS2Gen.RSSItem(
                title = data.title,
                link = data.link,
                description = data.description
                ))

        rss = PyRSS2Gen.RSS2(
            title = '3DMGAME',
            link = 'http://www.3dmgame.com/',
            description = u'3DMGAME以最专业的游戏新闻中心, 攻略中心, 最强的游戏改造和汉化能力, 最强大的游戏论坛为重要组成部分,拥有全国最大的单机游戏平台, 成为游戏玩家首要选择的游戏资讯门户网站.'
            )
        rss.items = itemList
        return rss.to_xml('utf-8')

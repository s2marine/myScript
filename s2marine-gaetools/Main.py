# -*- encoding:utf-8 -*-
import sys
sys.path.append('./lib/')
sys.path.append('./RSS/')
import webapp2
from page404 import page404
from page410 import page410
from pageRSSCronUpdate import pageRSSCronUpdate
from pageBilibiliSP import pageBilibiliSP
from pageBilibili import pageBilibili
from pageDuanziEveryday import pageDuanziEveryday
from pageChengyi import pageChengyi
from pageChengyiTimetable import pageChengyiTimetable
from pagePushCheck import pagePushCheck

class pageMain(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('s2marine-gaetools')

class mainUpdate(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('update')

class testConnection(webapp2.RequestHandler):
    def get(self):
        import requests
        url = self.request.get('url')
        html = requests.get(url)
        self.response.out.write(html.content)
        
class testConnection1(webapp2.RequestHandler):
    def get(self):
        import requests
        url = u'http://cyjwb.jmu.edu.cn/lists.asp?lbm=%CD%A8%D6%AA%B9%AB%B8%E6'
        html = requests.get(url)
        self.response.out.write(html.content)

class testConnection2(webapp2.RequestHandler):
    def get(self):
        import requests
        url = u'http://chengyi.jmu.edu.cn/NewsList.aspx?level=2&type=通知通告'
        html = requests.get(url)
        self.response.out.write(html.content)

app = webapp2.WSGIApplication([
                               ('/testConnection', testConnection),
                               ('/testConnection1', testConnection1),
                               ('/testConnection2', testConnection2),
                               ('/RSS/cronUpdate', pageRSSCronUpdate),
                               ('/RSS/BilibiliSP', pageBilibiliSP),
                               ('/RSS/bilibiliSP', page410),
                               ('/RSS/Bilibili', pageBilibili),
                               ('/RSS/bilibili', page410),
                               ('/RSS/DuanziEveryday', pageDuanziEveryday),
                               ('/RSS/Chengyi', pageChengyi),
                               ('/RSS/ChengyiTimetable', pageChengyiTimetable),
                               ('/RSS/pageDuanziEveryday', page410),
                               ('/RSS/baiduPan', page410),
                               ('/RSS/PushCheck', pagePushCheck),
                               ('/mainUpdate', mainUpdate),
                               ('/.+', page404),
                               ('/', pageMain)],
                               debug=True)

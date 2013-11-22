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
from pageJandan import pageJandan
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
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60)
        urls = []
        urls.append(u'http://cyjwb.jmu.edu.cn/lists.asp?lbm=%CD%A8%D6%AA%B9%AB%B8%E6')
        urls.append(u'http://chengyi.jmu.edu.cn/NewsList.aspx?level=2&type=通知通告')
        urls.append(u'http://cytyjys.jmu.edu.cn/Info/?id=2')
        urls.append("http://cyjwgl.jmu.edu.cn/ViewSchedule/ViewClassSchedule.aspx")
        for url in urls:
            s = requests.session()
            r = s.get(url)
            src = r.content
            self.response.out.write(url+'<br/>'+str(r.ok)+'<br/>')

app = webapp2.WSGIApplication([
                               ('/testConnection', testConnection),
                               ('/RSS/Jandan', pageJandan),
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

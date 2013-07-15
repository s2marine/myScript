#coding:utf-8
import webapp2
from page404 import page404
from RSS.page3DM import page3DM
from RSS.pageBilibili import pageBilibili
from RSS.page3DMUpdata import page3DMUpdata
from RSS.pageBilibiliUpdata import pageBilibiliUpdata
from RSS.pageBilibiliSP import pageBilibiliSP
from RSS.pageDuanziEveryday import pageDuanziEveryday
from Add2Pocket import Add2Pocket


class pageMain(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('s2marine-gaetools')

app = webapp2.WSGIApplication([('/RSS/3DM', page3DM),
                               ('/RSS/bilibili', pageBilibili),
                               ('/RSS/bilibiliSP', pageBilibiliSP),
                               ('/RSS/3DMUpdata', page3DMUpdata),
                               ('/RSS/bilibiliUpdata', pageBilibiliUpdata),
                               ('/RSS/pageDuanziEveryday', pageDuanziEveryday),
                               ('/Add2Pocket', Add2Pocket),
                               ('/.+', page404),
                               ('/', pageMain)],
                              debug=True)

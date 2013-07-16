#coding:utf-8
import webapp2
from page404 import page404
from RSS.page3DM import page3DM
from RSS.pageCyjwb import pageCyjwb
from RSS.pageBilibili import pageBilibili
from RSS.page3DMUpdate import page3DMUpdate
from RSS.pageBilibiliUpdate import pageBilibiliUpdate
from RSS.pageBilibiliSP import pageBilibiliSP
from RSS.pageDuanziEveryday import pageDuanziEveryday
from Add2Pocket import Add2Pocket
from RSS.pageCyjwbUpdate import UpdateCyjwb

class pageMain(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('s2marine-gaetools')

class mainUpdate(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        UpdateCyjwb()
        self.response.out.write('update')

app = webapp2.WSGIApplication([('/RSS/3DM', page3DM),
                               ('/RSS/cyjwb', pageCyjwb),
                               ('/RSS/bilibili', pageBilibili),
                               ('/RSS/bilibiliSP', pageBilibiliSP),
                               ('/RSS/bilibiliUpdate', pageBilibiliUpdate),
                               ('/RSS/pageDuanziEveryday', pageDuanziEveryday),
                               ('/Add2Pocket', Add2Pocket),
                               ('/mainUpdate', mainUpdate),
                               ('/.+', page404),
                               ('/', pageMain)],
                              debug=True)

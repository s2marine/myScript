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

class test(webapp2.RequestHandler):
    def get(self):
        from google.appengine.api import urlfetch
        import urllib
        import logging
        hub_url = 'https://pubsubhubbub.appspot.com/'
        hubUrl = self.request.get('url')
        data = urllib.urlencode({
            'hub.url': hubUrl,
            'hub.mode': 'publish'})
        response = urlfetch.fetch(hub_url, data, urlfetch.POST)
        logging.info("url is %s code is %d" % (hubUrl, response.status_code))
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("url is %s code is %d" % (hubUrl, response.status_code))

app = webapp2.WSGIApplication([
                               ('/test', test),
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

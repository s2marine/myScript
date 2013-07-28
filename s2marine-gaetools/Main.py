# -*- encoding:utf-8 -*-
import sys
sys.path.append('./lib/')
sys.path.append('./RSS/')
import webapp2
from page404 import page404
from pageRSSCronUpdate import pageRSSCronUpdate
from pageBilibiliSP import pageBilibiliSP

class pageMain(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('s2marine-gaetools')

class mainUpdate(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('update')

app = webapp2.WSGIApplication([
                               ('/RSS/cronUpdate', pageRSSCronUpdate),
                               ('/RSS/BilibiliSP', pageBilibiliSP),
                               ('/mainUpdate', mainUpdate),
                               ('/.+', page404),
                               ('/', pageMain)],
                               debug=True)

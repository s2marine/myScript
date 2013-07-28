# -*- encoding:utf-8 -*-
import webapp2
class page404(webapp2.RequestHandler):
    def get(self):
        self.abort(400, u'没有这个网站啦，求你们不要来抓了')

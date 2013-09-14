# -*- encoding:utf-8 -*-
import webapp2
class page410(webapp2.RequestHandler):
    def get(self):
        self.abort(410)

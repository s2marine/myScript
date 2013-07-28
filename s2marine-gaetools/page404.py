# -*- encoding:utf-8 -*-
import webapp2
class page404(webapp2.RequestHandler):
    def get(self):
        self.abort(404)

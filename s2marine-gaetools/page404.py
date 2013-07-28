# -*- encoding:utf-8 -*-
import webapp2
class page404(webapp2.RequestHandler):
    def get(self):
        self.response.set_status(404)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('404')

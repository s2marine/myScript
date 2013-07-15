#coding:utf-8
import webapp2
import urllib2


class Add2Pocket(webapp2.RequestHandler):
    def get(self):
        re = self.getRe()
        self.response.out.write(re)
    def getRe(self):
        username = self.request.get('username')
        password = self.request.get('password')
        url = self.request.get('url')
        callback = self.request.get('callback')
        apikey = '458TbSb6g21b9H4025d84f6B99p7GG83'
        req = 'https://readitlaterlist.com/v2/add?username='+username+'&password='+password+'&apikey='+apikey+'&url='+url
        return callback+'("'+urllib2.urlopen(req).read()+'")'

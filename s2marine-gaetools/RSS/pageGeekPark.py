#coding:utf-8
import webapp2
import PyRSS2Gen
import BeautifulSoup
import urllib2
import HTMLParser


class pageGeekPark(webapp2.RequestHandler):
    def get(self):
        rss = self.getRSS()
        self.response.out.write(rss)
    def getRSS(self):
        url = u'http://feeds.geekpark.net'
        src = urllib2.urlopen(url).read()
        soup = BeautifulSoup.BeautifulSoup(src)
        items = soup.findAll('item')
        [i.extract() for i in items if i.title.string[0:6]!=u'【极客观察】']
        html_parser = HTMLParser.HTMLParser()
        for i in items:
            i.description.string = html_parser.unescape(i.description.string)
        return soup

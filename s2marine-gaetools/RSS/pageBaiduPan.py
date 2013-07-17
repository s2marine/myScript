#coding=utf-8
import webapp2
import PyRSS2Gen
import BeautifulSoup
import urllib2
import urllib
import json
from google.appengine.api import urlfetch
import datetime

class pageBaiduPan(webapp2.RequestHandler):
    def get(self):
        self.shareid = self.request.get('shareid')
        self.uk = self.request.get('uk')
        self.path = self.request.get('dir/path')
        if not self.shareid:
            self.response.out.write(u'缺少shareid')
            return
        if not self.uk:
            self.response.out.write(u'缺少uk')
            return
        if not self.path:
            self.response.out.write(u'缺少dir/path')
            return
        self.title = self.path.split('/')[-1]
        rss = self.getRSS()
        self.response.out.write(rss)

    def getRSS(self):
        urlfetch.set_default_fetch_deadline(60)
        jsonUrl = 'http://pan.baidu.com/share/list?%s'
        data =  urllib.urlencode({'dir':self.path.encode('utf-8'), 'uk':self.uk, 'shareid':self.shareid})
        src = urllib2.urlopen(jsonUrl % data).read()
        files = json.loads(src)['list']
        files = sorted(files, key=lambda k: k['mtime'], reverse=True)

        itemList = []
        for i in files:
            if 'thumbs' in i:
                img = i['thumbs']['url3']
                descriptionadd = '<img src="'+img+'"></br>'
            else:
                descriptionadd = ''
            descriptionadd += '<a href="'+i['dlink']+u'">下载</a>'
            itemList.append(PyRSS2Gen.RSSItem(
                title = i['server_filename'],
                link = i['dlink'],
                guid = PyRSS2Gen.Guid(i['dlink']), 
                description = descriptionadd
                ))

        data =  urllib.urlencode({'uk':self.uk, 'shareid':self.shareid})
        fragment = urllib.urlencode({'path':self.path.encode('utf-8')}).replace('+', '%20')
        pageUrl = 'http://pan.baidu.com/share/link?%s#dir/%s' % (data, fragment)
        rss = PyRSS2Gen.RSS2(
            title = self.title,
            link = pageUrl,
            description = ''
            )
        rss.items = itemList
        return rss.to_xml('utf-8')

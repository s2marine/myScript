#coding:utf-8
import webapp2
from google.appengine.ext import db
import BeautifulSoup
import PyRSS2Gen
import urllib2
import re
import json

class DBBILIBILI(db.Model):
    title = db.StringProperty(multiline=True)
    link = db.StringProperty(multiline=True)
    description = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)

def updataBilibili():
    source = urllib2.urlopen('http://www.bilibili.tv/index/ranking.json').read()
    data = json.loads(source)['hot']['list']

    oldDB = db.GqlQuery('SELECT * FROM DBBILIBILI')
    db.delete(oldDB)

    list = []
    for i in range(0, 10):
        titleadd = data[str(i)]['title']
        linkadd = 'http://www.bilibili.tv/video/av'+str(data[str(i)]['aid'])+'/'
        descriptionadd = '<img src="'+data[str(i)]['pic']+'"/>'
        list.append({'title':titleadd, 'link':linkadd, 'description':descriptionadd})

    for i in list[::-1]:
        database = DBBILIBILI()
        database.title = i['title']
        database.link = i['link']
        database.description = i['description']
        database.put()

'''
def get3DMPost(link):
    source = urllib2.urlopen(link).read().decode('GBK')
    soup = BeautifulSoup.BeautifulSoup(source)
    post = soup.find('div', attrs={'class':'DeContentBOttom'})
    [each.extract() for each in post.findAll('div', attrs={'align':'center'})]
    [each.extract() for each in post.findAll('img')]
    return post.prettify().decode('utf-8')
'''

class pageBilibiliUpdata(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        updataBilibili()
        self.response.out.write('updata')

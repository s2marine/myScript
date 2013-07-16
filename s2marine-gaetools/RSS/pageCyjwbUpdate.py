#coding:utf-8
import webapp2
from google.appengine.ext import db
import BeautifulSoup
import PyRSS2Gen
import urllib2
import re
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(600)

MAX_RSS_ITEM = 10

class DBCyjwb(db.Model):
    title = db.StringProperty(multiline=True)
    link = db.StringProperty(multiline=True)
    description = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)

def UpdateCyjwb():
    source = urllib2.urlopen('http://cyjwb.jmu.edu.cn/lists.asp?lbm=%CD%A8%D6%AA%B9%AB%B8%E6').read()
    soup = BeautifulSoup.BeautifulSoup(source)
    newList = soup.findAll('table')[2].findAll('a', attrs={'target':'_blank'})

    oldDB = db.GqlQuery('SELECT * FROM DBCyjwb ORDER BY date DESC')
    count = oldDB.count()
    oldLinkList = [data.link for data in oldDB]
    list = []
    p = re.compile(r'^\s*?\d+?\.\d+? ')
    for i in newList[:MAX_RSS_ITEM]:
        titleadd = i.text
        linkadd = 'http://cyjwb.jmu.edu.cn/'+i['href']

        if linkadd in oldLinkList:
            continue
        list.append({'title':titleadd, 'link':linkadd})
    


    for i in list[::-1]:
        database = DBCyjwb()
        database.title = i['title']
        database.link = i['link']
        database.description = getCyjwbPost(i['link'])
        return i['link']+database.description
        database.put()
        count += 1

    if count-MAX_RSS_ITEM > 0:
        deleteTimes = count-MAX_RSS_ITEM
        deleteDB = db.GqlQuery('SELECT * FROM DBCyjwb ORDER BY date LIMIT '+str(deleteTimes))
        db.delete(deleteDB)

def getCyjwbPost(link):
    source = urllib2.urlopen(link).read()
    soup = BeautifulSoup.BeautifulSoup(source)
    post = soup.find(attrs={'id':'zoom'})
    return post
    #return post.prettify()

class pageCyjwbUpdate(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        UpdateCyjwb()
        self.response.out.write('Update')

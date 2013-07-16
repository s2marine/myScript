#coding:utf-8
import webapp2
from google.appengine.ext import db
import BeautifulSoup
import PyRSS2Gen
import urllib2
import re

MAX_RSS_ITEM = 50

class DB3DM(db.Model):
    title = db.StringProperty(multiline=True)
    link = db.StringProperty(multiline=True)
    description = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)

def updata3DM():
    source = urllib2.urlopen('http://www.3dmgame.com').read().decode('GBK')
    source = source.replace('&nbsp;', ' ')
    soup = BeautifulSoup.BeautifulSoup(source)
    newList = soup.find(attrs={'id':'tab_two_1'}).contents[3].findAll('a')

    oldDB = db.GqlQuery('SELECT * FROM DB3DM ORDER BY date DESC')
    count = oldDB.count()
    oldTitleList = [data.title for data in oldDB]
    list = []
    p = re.compile(r'^\s*?\d+?\.\d+? ')
    for i in newList:
        if len(i)==3:
            titleadd = i.contents[1].contents[0].string.encode('utf-8')
            linkadd = i['href']
        else:
            titleadd = i.contents[0].string.encode('utf-8')
            linkadd = i['href']
        titleadd = str(p.sub('', titleadd).strip()).decode('utf-8')
        linkadd = str(p.sub('', linkadd).strip().decode('utf-8'))

        if titleadd in oldTitleList:
            continue
        list.append({'title':titleadd, 'link':linkadd})


    for i in list[::-1]:
        database = DB3DM()
        database.title = i['title']
        database.link = i['link']
        database.description = ' '
        database.put()
        count += 1

    if count-MAX_RSS_ITEM > 0:
        deleteTimes = count-MAX_RSS_ITEM
        deleteDB = db.GqlQuery('SELECT * FROM DB3DM ORDER BY date LIMIT '+str(deleteTimes))
        db.delete(deleteDB)

'''
def get3DMPost(link):
    source = urllib2.urlopen(link).read().decode('GBK')
    soup = BeautifulSoup.BeautifulSoup(source)
    post = soup.find('div', attrs={'class':'DeContentBOttom'})
    [each.extract() for each in post.findAll('div', attrs={'align':'center'})]
    [each.extract() for each in post.findAll('img')]
    return post.prettify().decode('utf-8')
'''

class page3DMUpdata(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        updata3DM()
        self.response.out.write('updata')

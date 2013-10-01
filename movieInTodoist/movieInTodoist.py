#!/usr/bin/env python3
# -*- encoding:utf-8 -*-
import re
import sys
import json
import time
import queue
import threading
import urllib.parse
import requests
from bs4 import BeautifulSoup

doubanToken='0a7c06be1f447e761f74143a5dcd7b62'
tomatoToken='5rpbjyyuwqmyj4t97b6buft8'
todoistToken='72c10592f98d5a6c605a591d5a72b97ddc137f3b'
#todoistToken='f740e16f33a1c7f76846f45474d156823f039a8f'
projectID='1054422'
#projectID='108537458'
proxy={"http":"127.0.0.1:8087"}


def getDoubanByIMDBID(IMDBID):
    print(sys._getframe().f_code.co_name, IMDBID)
    '''
    http://api.douban.com/v2/movie/search?q=tt1832382
    '''
    data = urllib.parse.urlencode({'q':IMDBID, 'apikey':doubanToken})
    r = requests.get('http://api.douban.com/v2/movie/search?%s' % data)
    return json.loads(r.text)['subjects'][0]

def getIMDBByIMDBID(IMDBID):
    print(sys._getframe().f_code.co_name, IMDBID)
    '''
    http://www.omdbapi.com/?i=tt0119698
    '''
    r = requests.get('http://www.omdbapi.com/?i=%s' % IMDBID)
    return json.loads(r.text)

def getTomatoesByIMDBID(IMDBID):
    print(sys._getframe().f_code.co_name, IMDBID)
    '''
    http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?apikey=5rpbjyyuwqmyj4t97b6buft8&type=imdb&id=0816711
    '''
    data = urllib.parse.urlencode({'apikey':tomatoToken, 'type':'imdb', 'id':IMDBID[2:]})
    r = requests.get('http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?%s' % data, proxies=proxy)
    result = json.loads(r.text)
    if 'error' in result:
        return False
    else:
        return result

def getReleaseDate(titleEN, year):
    print(sys._getframe().f_code.co_name, titleEN, year)
    '''
    http://www.blu-ray.com/search/quicksearch.php
    '''
    r = requests.post('http://www.blu-ray.com/search/quicksearch.php', 
            data={
                'section':'bluraymovies', 
                'userid':-1, 
                'country':'US', 
                'keyword':titleEN
                }, proxies=proxy)
    soup = BeautifulSoup(r.content)
    for i in soup.findAll('li'):
        strAll = i.findAll(text=True)[1].strip()
        strYear = re.search('\((\d{4})\)', strAll).group(1)
        strTitle = re.sub('\(.*?\)', '', strAll).strip()
        print(strTitle)
        if titleEN!=strTitle or int(strYear)!=int(year):
            continue
        strTime = i.find('span').text
        if strTime=='-':
            return False
        struct_t = time.strptime(strTime, "%b %d, %Y")
        return struct_t
        #return time.strftime("%Y-%m-%d", struct_t)

def getInfoFromTodoist(token, projectID):
    print(sys._getframe().f_code.co_name)
    data = {'token':todoistToken, 'project_id':projectID}
    r = requests.post('http://todoist.com/API/getUncompletedItems', data=data, proxies=proxy)
    movieInfos = [{'id':i['id'], 'content':i['content']} for i in json.loads(r.text)]
    return movieInfos

class GetMovieInfos(threading.Thread):
    def __init__(self, input, worktype):
        self._jobq = input
        self._work_type = worktype
        threading.Thread.__init__(self)
    def run(self):
        while not self._jobq.empty():
            job = self._jobq.get()
            worktype=self._work_type
            self._process_job(job, worktype)
    def _process_job(self, job, worktype):
        getMovieInfo(job)
        self._jobq.task_done()

def getMovieInfo(movieInfo):
    IMDBID = re.search('tt\d{7}', movieInfo['content']).group()
    print(IMDBID)
    movieInfo['IMDBID'] = IMDBID
    doubanSrc = getDoubanByIMDBID(IMDBID)
    if doubanSrc:
        movieInfo['titleCN'] = doubanSrc['title']
        movieInfo['douban'] = doubanSrc['rating']['average']
    tomatoData = getTomatoesByIMDBID(IMDBID)
    if tomatoData:
        movieInfo['tomato'] = tomatoData['ratings']['critics_score']
    IMDBData = getIMDBByIMDBID(IMDBID)
    if IMDBData:
        movieInfo['titleEN'] = IMDBData['Title']
        movieInfo['year'] = IMDBData['Year']
        movieInfo['IMDB'] = IMDBData['imdbRating']
    movieInfo['releaseDate'] = getReleaseDate(movieInfo['titleEN'], movieInfo['year'])

def connectMovieInfo(movieInfos):
    result = []
    for movieInfo in movieInfos:
        item = {}
        item['id'] = movieInfo['id']

        movieInfo['titleCN'] = movieInfo.get('titleCN') or ''
        movieInfo['titleEN'] = movieInfo.get('titleEN') or ''
        movieInfo['year'] = str(movieInfo.get('year')) or ''
        movieInfo['IMDB'] = 'IMDB:'+str(movieInfo.get('IMDB')) or ''
        movieInfo['tomato'] = '烂番茄'+str(movieInfo.get('tomato')) or ''
        movieInfo['douban'] = '豆瓣:'+str(movieInfo.get('douban')) or ''
        movieInfo['IMDBID'] = movieInfo.get('IMDBID') or ''
        if movieInfo.get('releaseDate') and movieInfo['releaseDate']>time.gmtime():
            movieInfo['releaseDate'] = time.strftime("%Y-%m-%d", movieInfo['releaseDate'])
            item['priority'] = 4
        else:
            movieInfo['releaseDate'] = ''
            item['priority'] = 1

        item['content'] = '	'.join((movieInfo['titleCN'], 
                movieInfo['titleEN'],
                movieInfo['year'],
                movieInfo['IMDB'],
                movieInfo['tomato'],
                movieInfo['douban'],
                movieInfo['IMDBID'],
                movieInfo['releaseDate'],))
        print(item['content'])

        result.append({'type':'item_update', 'args':item})
    return result



def main():
    movieInfos = getInfoFromTodoist(todoistToken, projectID)
    q = queue.Queue(0) 
    for i in movieInfos:
        q.put(i)
    for x in range(10):
        GetMovieInfos(q, x).start()
    q.join()
    result = connectMovieInfo(movieInfos)
    j = json.dumps(result)
    data = {'api_token':todoistToken, 'items_to_sync':j}
    r = requests.post('http://api.todoist.com/TodoistSync/v2/sync', data=data)

if __name__=='__main__':
    main()

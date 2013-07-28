# -*- encoding:utf-8 -*-
import sys
sys.path.append('./lib/')
sys.path.append('./RSS/')
import webapp2
from google.appengine.ext import db
import json
import datetime
from RSSClass import *


class pageRSSCronUpdate(webapp2.RequestHandler):
    def get(self):
        self.getCronList()
        self.analysisCronList()
        self.response.out.write('RSSCronUpdate')

    def getCronList(self):
        crons = db.GqlQuery('SELECT * FROM DBRSSCron').fetch(None)
        self.crons = crons
        return crons

    def analysisCronList(self):
        for cron in self.crons:
            if cron.isTime():
                rssClass = __import__("page"+cron.RSSName)
                rssObject = getattr(rssClass, "RSS"+cron.RSSName)
                o = rssObject(cron.getUrlArgs())
                o.cronUpdate(cron)

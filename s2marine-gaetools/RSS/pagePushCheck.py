# -*- encoding:utf-8 -*-
import sys
import logging
import re
sys.path.append('./lib/')
sys.path.append('./RSS/')
import webapp2
from google.appengine.ext import db
import json
import datetime
from RSSClass import *


class pagePushCheck(webapp2.RequestHandler):
    def get(self):
        mode = self.request.get('hub.mode')
        topic = self.request.get('hub.topic')
        challenge = self.request.get('hub.challenge')
        self.response.out.write(challenge)
        logging.info("%s: %s" % (mode, topic))
    def post(self):
        link = re.search('<link>(.+?)</link>', self.request.body).group(1)
        logging.info("pushed: %s" % (link))

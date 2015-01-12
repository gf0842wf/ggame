# -*- coding: utf-8 -*-
from path import HOME_DIR
from settings import settings
from copy import deepcopy
import pymongo
import os

settings.load(os.path.join(HOME_DIR, 'etc/web/taihe_test.json'))

monconf = deepcopy(settings['MONGO'])
db = monconf.pop('db')
monconf['host'] = str(monconf['host'])
mondb = pymongo.MongoClient(use_greenlets=True, **monconf)[db]

users = [{'username':'111', 'password':'111'}, 
         {'username':'222', 'password':'222'},
         {'username':'333', 'password':'333'},
         {'username':'444', 'password':'444'},
         {'username':'555', 'password':'555'}
         ]

mondb.user.insert(users)
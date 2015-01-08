# -*- coding: utf-8 -*-
from copy import deepcopy
from gnet.client import Client
from gnet.db.gmy import Pool as MyPool
from .settings import settings


client = Client()

myconf = deepcopy(settings['MYSQL'])
n = myconf.pop('n')
reconnect_delay = myconf.pop('reconnect_delay')
mypool = MyPool(myconf, n, reconnect_delay)

client.add_client('mysql_client', mypool)
# client['mysql_client'].fetchone

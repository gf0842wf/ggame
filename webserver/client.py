# -*- coding: utf-8 -*-
"""所有客户端统一管理(db,rpc等)"""

from copy import deepcopy
from gnet.client import Client
from .settings import settings

from gnet.db.gmy import Pool as MyPool
import mprpc
import gsocketpool.pool

import pymongo


# class MPRPCClient(object):
#     def __init__(self, mprpcpool):
#         self.mprpcpool = mprpcpool
#     
#     def call(self, method, *args):
#         with self.mprpcpool.connection() as client:
#             return client.call(method, *args)
        

client = Client()

'''
myconf = deepcopy(settings['MYSQL'])
# myconf.update({'autocommit':False}) # 默认autocommit为True,当使用事务时,使用query('SET AUTOCOMMIT=0')临时关闭自动提交
n = myconf.pop('n')
reconnect_delay = myconf.pop('reconnect_delay')
mypool = MyPool(myconf, n, reconnect_delay)

client.add_client('mysql_client', mypool)
# client['mysql_client'].fetchone

rpcconf = deepcopy(settings['RPC'])
n = rpcconf.pop('n')
gpool = gsocketpool.pool.Pool(mprpc.RPCPoolClient, options=rpcconf, initial_connections=n)
mprpcpool = MPRPCClient(gpool)
 
client.add_client('rpc_client', mprpcpool)
# client['rpc_client'].call
'''

monconf = deepcopy(settings['MONGO'])
db = monconf.pop('db')
monconf['host'] = str(monconf['host'])
mondb = pymongo.MongoClient(use_greenlets=True, **monconf)[db]  # 这里有个问题,MongoClient的host参数只接受 basestring,而经过dump后的配置是unicode的,所以需要转换一下

client.add_client('mongo_client', mondb)
# client['mongo_client'].find_one


# -*- coding: utf-8 -*-
from copy import deepcopy
from gnet.client import Client
from gnet.db.gmy import Pool as MyPool
from .settings import settings
import mprpc
import gsocketpool.pool


# class MPRPCClient(object):
#     def __init__(self, mprpcpool):
#         self.mprpcpool = mprpcpool
#     
#     def call(self, method, *args):
#         with self.mprpcpool.connection() as client:
#             return client.call(method, *args)
        

client = Client()

'''先不使用mysql和rpc
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

# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()
from gnet.rpcprotocol import MPRPCServerFactory
import logging
import mprpc

logger = logging.getLogger(__name__)


class RPCProtocol(mprpc.RPCServer):
    '''rpc 任务'''
    
    def sum(self, x, y):
        return x + y
    

class RPCServerFactory(MPRPCServerFactory):
    
    def __init__(self, addr):
        super(RPCServerFactory, self).__init__(addr, RPCProtocol)

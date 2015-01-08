# -*- coding: utf-8 -*-
'''rpc protocol & factory'''

import gevent.server
import logging

logger = logging.getLogger(__name__)


class MPRPCServerFactory(gevent.Greenlet):
    '''mprpc server factory'''
    
    def __init__(self, addr, rpcserver_handler):
        self.addr = addr
        self.rpcserver_handler = rpcserver_handler
        gevent.Greenlet.__init__(self)
        
    def on_notify(self, *args, **kwargs):
        '''作为观察者的回调,在service中调用'''
        raise NotImplementedError
    
    def _run(self):
        server = gevent.server.StreamServer(self.addr, self.rpcserver_handler)
        logger.info('mprpc server listen @ %s', str(self.addr))
        server.serve_forever()

# -*- coding: utf-8 -*-
'''rpc client/db client的实例统一管理
: 一般情况client先于service启动(因为client供service调用)
'''

from .util import Singleton
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class Client(Singleton):
    ''' 客户端集合类
    1.统一管理client (pool)等
    2.单例模式: Client是单例的
    '''
    
    _clients = {}
    
    def add_client(self, name, client):
        if self._clients is {}:
            self._clients = OrderedDict()
            
        assert name not in self._clients
        
        self._clients[name] = client
        
        return client
    
    def get_client(self, name):
        return self._clients.get(name, None)
        
    def remove_client(self, name):
        return self._clients.pop(name, None)
    
    def __getitem__(self, name):
        return self._clients.get(name, None)
    
    def __setitem__(self, name, client):
        if self._clients is None:
            self._clients = OrderedDict()
            
        assert name not in self._clients
        
        self._clients[name] = client
        
        return client
    
    def __delitem__(self, name):
        return self._clients.pop(name, None)
    
    def start(self):
        logger.info('client manager start')
        
    def notify_client(self, name, cb_name, *args, **kwargs):
        '''通知 client
        @param name: 通知到的client, eg. '*' - 全部通知, 'f1'-通知单个client, ['c1', 'c2']-通知多个client
        @param cb: 调用client的回调函数名字
        '''
        
        names = []
        if isinstance(name, list):
            names = name
        elif isinstance(name, str):
            if name == '*':
                names = self._clients.keys()
            else:
                names = [name]
                
        for name in names:
            client = self._clients[name]
            getattr(client, cb_name)(*args, **kwargs)  # 没有进行是否存在cb_name判断
    



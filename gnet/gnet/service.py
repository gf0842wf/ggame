# -*- coding: utf-8 -*-
from .util import Singleton
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class Service(Singleton):
    ''' 服务类
    1.统一管理server factory/client factory等
    2.观察者模式: 通过service向factory通信
    3.单例模式: Service是单例的
    '''
    
    _factorys = {}
    
    def add_factory(self, name, factory):
        if self._factorys is {}:
            self._factorys = OrderedDict()
            
        assert name not in self._factorys
        
        self._factorys[name] = factory
        
        return factory
    
    def get_factory(self, name):
        return self._factorys.get(name, None)
        
    def remove_factory(self, name):
        return self._factorys.pop(name, None)
    
    def __getitem__(self, name):
        return self._factorys.get(name, None)
    
    def __setitem__(self, name, factory):
        if self._factorys is None:
            self._factorys = OrderedDict()
            
        assert name not in self._factorys
        
        self._factorys[name] = factory
        
        return factory
    
    def __delitem__(self, name):
        return self._factorys.pop(name, None)
    
    def start(self):
        logger.info('service manager start')
        [f.start() for f in self._factorys.values()]
        
    def notify_factory(self, name, *args, **kwargs):
        '''通知 factory
        @param name: 通知到的factory, eg. '*' - 全部通知, 'f1'-通知单个factory, ['f1', 'f2']-通知多个factory
        '''
        
        names = []
        if isinstance(name, list):
            names = name
        elif isinstance(name, str):
            if name == '*':
                names = self._factorys.keys()
            else:
                names = [name]
                
        for name in names:
            self._factorys[name].on_notify(*args, **kwargs)
    

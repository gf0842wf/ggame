# -*- coding: utf-8 -*-
from collections import OrderedDict


class Manager(OrderedDict):
    '''对象管理器

    用法::

        manager = Manager()

        manager.register(1, 'ONE')

        @manager.register
        def a(): pass

        @manager.named('funcb', 'FUNCB')
        def b(): pass

        @manager.register
        class A: pass

        @manager.named('clsb', 'CLSB')
        class B: pass
    '''
    def register(self, ob, name=None):
        if not name:
            name = ob.__name__
        assert name not in self
        self[name] = ob
        return ob

    def named(self, *names):
        def func(ob):
            for name in names:
                self[name] = ob
            return ob
        return func

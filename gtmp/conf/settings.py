# -*- coding: utf-8 -*-
from pu.dictutil import DotOrderedDict
from pu.pattern.singleton import Singleton
import json


class Settings(DotOrderedDict):
    __metaclass__ = Singleton
    
    def load(self, filename):
        try:
            self.update(json.load(open(filename), encoding='utf-8'))
        except:
            self.update(eval(open(filename).read()))


settings = Settings()
# -*- coding: utf-8 -*-
'''所有服务器统一管理'''
from gnet.service import Service
from .web import WebServerFactory
from .settings import settings

service = Service()
service.add_factory('web_server', WebServerFactory((settings['WEB']['host'], settings['WEB']['port'])))

# -*- coding: utf-8 -*-
from gnet.service import Service
from .gate import GateServerFactory
from .settings import settings

service = Service()
service.add_factory('gate_server', GateServerFactory((settings['GATE']['host'], settings['GATE']['port'])))

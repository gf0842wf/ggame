# -*- coding: utf-8 -*-
from gnet.service import Service
from .rpc import RPCServerFactory
from .settings import settings

root = Service()
root.add_factory('rpc_server', RPCServerFactory((settings['RPC']['host'], settings['RPC']['port'])))
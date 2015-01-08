# -*- coding: utf-8 -*-
from gnet.protocol import WSGIServerFactory
import geventwebsocket.handler
import sys
import logging

from .app import app

logger = logging.getLogger(__name__)


class WebServerFactory(WSGIServerFactory):

    def __init__(self, addr):
        self.addr = addr
        super(WebServerFactory, self).__init__(addr, app, handler_class=geventwebsocket.handler.WebSocketHandler, log=sys.stderr)

# -*- coding: utf-8 -*-
from gnet.protocol import HookLogWSHandler, WSGIServerFactory
import sys
import logging

from .app import app

logger = logging.getLogger(__name__)


class WebServerFactory(WSGIServerFactory):

    def __init__(self, addr):
        self.addr = addr
        super(WebServerFactory, self).__init__(addr, app, handler_class=HookLogWSHandler, log=sys.stderr)

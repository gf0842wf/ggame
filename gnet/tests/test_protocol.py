# -*- coding: utf-8 -*-
from gnet.protocol import TCPServerFactory, ReconnectingClientFactory, Protocol
from gnet.util import shorten
import gevent
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)-15s %(levelname)s:%(module)s] %(message)s')


class EchoServerProtocol(Protocol):

    def connection_made(self):
        logger.info('connection made')

    def data_received(self, data):
        logger.debug('data received: %s', shorten(data, 32))
        self.send_data(data)

    def connection_lost(self, reason):
        logger.info('connection lost')
        super(EchoServerProtocol, self).connection_lost(reason)


class EchoServerFactory(TCPServerFactory):

    def build_protocol(self, sock, addr):
        logger.info('connection handler %s', str(addr))
        p = EchoServerProtocol(sock, addr)
        p.factory = self
        return p

sf = EchoServerFactory(('127.0.0.1', 6011))
sf.start()


class EchoClientProtocol(Protocol):

    def connection_made(self):
        logger.info('connection made')
        self.send_data('ooxx')

    def data_received(self, data):
        logger.debug('data received: %s', shorten(data, 32))
        self.send_data(data)
        gevent.sleep(2)

    def connection_lost(self, reason):
        logger.info('connection lost')
        super(EchoClientProtocol, self).connection_lost(reason)


class EchoClientFactory(ReconnectingClientFactory):

    reconnect_delay = 10

    def build_protocol(self, sock, addr):
        logger.info('connection handler %s', str(addr))
        p = EchoClientProtocol(sock, addr)
        p.factory = self
        return p
    
cf = EchoClientFactory(('127.0.0.1', 6011))
cf.start()


gevent.wait()

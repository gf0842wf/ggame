# -*- coding: utf-8 -*-
from gnet.protocol import TCPServerFactory, ReconnectingClientFactory, Protocol
from gnet.util import shorten
import gevent
import logging

from gnet.service import Service

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)-15s %(levelname)s:%(module)s] %(message)s')


class EchoServerProtocol(Protocol):
    read_deadline = 20
    
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
    
    def on_notify(self, *args, **kwargs):
        print 'notify ---server---', args

sf = EchoServerFactory(('127.0.0.1', 6011))
# sf.start()


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
        
    def on_notify(self, *args, **kwargs):
        print 'notify ---client---', args

cf = EchoClientFactory(('127.0.0.1', 6011))
# cf.start()

root = Service()
root.add_factory('echo_server', sf).start()
root.add_factory('echo_client', cf).start()

root.notify_factory('*', "hello")
print root.get_factory('echo_server')

gevent.wait()

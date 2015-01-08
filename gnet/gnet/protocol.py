# -*- coding: utf-8 -*-
'''参照 twisted/asyncio重新设计下api
: 和dbprotocol/rpcprotocol的factory不同, 这里 reconnect_delay不作为__init__参数,而是通过重载时更改
'''

import gevent.monkey; gevent.monkey.patch_socket()
import logging

import gevent
import gevent.queue
import gevent.socket
import gevent.server

import sys
import gevent.pywsgi
# import geventwebsocket.handler

from .util import shorten

logger = logging.getLogger(__name__)

def id_generator():
    i = 0
    wall = 1 << 31
    while True:
        i += 1
        if i > wall:
            i = 1
        yield i

        
class ProtocolException(Exception):
    pass


class ProtocolTimeoutException(Exception):
    pass


class FactoryException(Exception):
    pass


class Protocol(gevent.Greenlet):

    recv_buf_size = 256
    read_deadline = 0 # 心跳超时: 0-不超时
    
    id_generator = id_generator()
    transport = None
    glet_recver = None
    glet_sender = None
    sendq = gevent.queue.Queue()  # 发送消息队列
    
    inner_glets = {}  # 生命周期在protocol协程之前的协程放在这里
    
    def __init__(self, transport, addr):
        self.transport = transport
        self.addr = addr
        gevent.Greenlet.__init__(self)
        
    def add_inner_glet(self, name, glet):
        self.inner_glets[name] = glet
        return glet
        
    def get_inner_glet(self, name):
        return self.inner_glets.get(name, None)
    
    def remove_inner_glet(self, name):
        return self.inner_glets.pop(name, None)
    
    def _run(self):
        self.make_connection(self.transport)
    
    def make_connection(self, transport):
        self.connected = True
        self.session_id = self.id_generator.next()
        self.transport = transport
        
        self.start_loop_sending()
        self.glet_recver = gevent.spawn(self.loop_recving)
        self.connection_made()
        
    def connection_made(self):
        logger.info('connection made')
    
    def data_received(self, data):
        logger.debug('data received: %s', shorten(data, 32))
     
    def connection_lost(self, reason):
        logger.info('connection lost: %s', reason)
    
    def start_loop_sending(self):
        '''开始循环发送: 通过队列,在一个单独协程中发送'''
        logger.info('start loop sending')
        self.glet_sender = gevent.spawn(self.loop_sending)
    
    def send_data(self, data):
        '''异步发送,必须是执行过start_loop_sending'''
        logger.debug('send data: %s', shorten(data, 32))
        self.sendq.put(data)
        
    def send_lose(self, data):
        '''发送消息然后断开'''
        self.send_rest()
        try:
            self.transport.sendall(data)
        except:
            logger.warn('send lose except', exc_info=1)
        self.close_protocol()
        
    def send_rest(self):
        '''把sendq队列里剩余的发完'''
        while not self.sendq.empty():
            data = self.sendq.get()
            try:
                self.transport.sendall(data)
            except:
                logger.warn('send one except', exc_info=1)
                self.close_protocol()
                break
            
    def pre_connection_lost(self, reason):
        if getattr(self.factory, 'reconnect_delay', 0) is not 0:
            # 这个针对重连客户端的
            try:
                self.factory.connection_lost(ProtocolException(reason))
            except:
                logger.info('pre connection lost except')
        else:
            self.connection_lost(reason)
        self.close_protocol()
    
    def loop_recving(self):
        reason = ''
        while True:
            try:
                if self.read_deadline is not 0:
                    with gevent.Timeout(self.read_deadline, ProtocolTimeoutException('msg timeout')):
                        data = self.transport.recv(self.recv_buf_size)
                else:
                    data = self.transport.recv(self.recv_buf_size)
            except Exception as e:
                self.transport = None
                if isinstance(e, ProtocolTimeoutException):
                    reason = 'msg timeout'
                logger.warn('loop recving except', exc_info=1)
                reason = 'loop recving except'
                break
            if not data:
                reason = 'loop recving none data'
                break
            self.data_received(data)
        self.pre_connection_lost(ProtocolException(reason))

    def loop_sending(self):
        reason = ''
        while True:
            data = self.sendq.get()
            try:
                self.transport.sendall(data)
            except:
                logger.warn('loop sending except', exc_info=1)
                reason = 'loop sending except'
                break
        self.pre_connection_lost(ProtocolException(reason))
    
    def close_protocol(self):
        try:
            self.glet_sender.kill()
        except:
            logger.info('greenlet sender kill except')
            
        self.send_rest()
        
        if self.transport:
            self.transport.close()
            self.transport = None
            
        try:
            if self.glet_recver: self.glet_recver.kill()
        except:
            logger.info('greenlet recver kill except')
        
        try:
            [g.kill() for g in self.inner_glets.values()]
        except:
            logger.info('inner greenlets kill except')
        
        try:
            self.kill()
        except:
            logger.info('self greenlet kill except')


class TCPServerFactory(gevent.Greenlet):
    
    protocol_cls = None  # 继承时可以给它赋值,或者重载 build_protocol
    
    def __init__(self, addr):
        self.addr = addr
        gevent.Greenlet.__init__(self)
        
    def on_notify(self, *args, **kwargs):
        '''作为观察者的回调,在service中调用'''
        raise NotImplementedError
    
    def build_protocol(self, sock, addr):
        logger.info('build protocol %s', str(addr))
        p = self.protocol_cls(sock, addr)
        p.factory = self
        return p
        
    def _connection_handler(self, sock, addr):
        p = self.build_protocol(sock, addr)
        p.start()
        
    def _run(self):
        server = gevent.server.StreamServer(self.addr, self._connection_handler)
        logger.info('tcp server listen @ %s', self.addr)
        server.serve_forever()
        
        
class ReconnectingClientFactory(gevent.Greenlet):
    
    protocol_cls = None  # 继承时可以给它赋值,或者重载 build_protocol
    protocol_obj = None
    
    reconnect_delay = 0  # 重连延时,0-不重连
    
    def __init__(self, addr):
        self.addr = addr
        gevent.Greenlet.__init__(self)
        
    def on_notify(self, *args, **kwargs):
        '''作为观察者的回调,在service中调用'''
        raise NotImplementedError
    
    def build_protocol(self, sock, addr):
        logger.info('build protocol %s', str(addr))
        self.protocol_obj = p = self.protocol_cls(sock, addr)
        p.factory = self
        return p
        
    def reconnect(self):
        while True:
            self.disconnect()
            try:
                logger.info('trying reconnect..')
                self.transport = transport = gevent.socket.create_connection(self.addr)
                logger.info('reconnected.')
                p = self.build_protocol(transport, self.addr)
                p.start()
                break
            except:
                logger.warn('reconnect except', exc_info=1)
            gevent.sleep(self.reconnect_delay)
            
    def disconnect(self):
        try:
            self.protocol_obj.close_protocol()
            self.protocol_obj.kill()
        except:
            logger.info('greenlet protocol kill except')
        
    def connection_lost(self, reason):
        '''会在protocol中被调用'''
        if self.reconnect_delay is not 0:
            self.reconnect()
            
    def _run(self):
        transport = gevent.socket.create_connection(self.addr)
        logger.info('tcp client connect to %s', str(self.addr))
        p = self.build_protocol(transport, self.addr)
        p.start()


class WSGIServerFactory(gevent.Greenlet):
    # handler_class = geventwebsocket.handler.WebSocketHandler 支持websocket的wsgi handler
    
    def __init__(self, addr, app=None, handler_class=gevent.pywsgi.WSGIHandler, log=sys.stderr):
        self.addr = addr
        self.app = app or self._app
        self.log = log
        self.handler_class = handler_class
        gevent.Greenlet.__init__(self)
        
    def on_notify(self, *args, **kwargs):
        '''作为观察者的回调,在service中调用'''
        raise NotImplementedError

    def _app(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield 'hello, world!'

    def _run(self):
        server = gevent.pywsgi.WSGIServer(self.addr,
                                          self.app,
                                          handler_class=self.handler_class,
                                          log=self.log)
        logger.info('wsgi&ws server listen @ %s', str(self.addr))
        server.serve_forever()
        
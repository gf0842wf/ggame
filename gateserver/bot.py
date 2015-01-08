# -*- coding: utf-8 -*-
'''一个模拟设备'''

from gnet.protocol import Protocol, ReconnectingClientFactory
import gevent
import logging

import codec.fixnh
import ujson
import xorcrypt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)-15s %(levelname)s:%(module)s] %(message)s')


class ClientProtocol(Protocol):
    read_deadline = 0
    
    def connection_made(self):
        # 初始化编解码器
        dumps = ujson.dumps
        loads = ujson.loads
            
        encrypt = xorcrypt.encrypt
        decrypt = xorcrypt.decrypt
        self.key = None
            
        self.codec = codec.fixnh.Codec(4, '>',
                                       dumps=dumps, loads=loads,
                                       encrypt=encrypt, decrypt=decrypt,
                                       factory=self
                                       )
        logger.info('connection made')

    def data_received(self, data):
        for _, msg in self.codec.decode(data):
            if msg is not None:
                self.message_received(msg)
                
    def message_received(self, message):
        logger.debug('message: %s', message)
        prefix = message.pop('type')
        handle = getattr(self, 'handle_%s' % prefix, None)
        if handle:
            handle(message)
            
    def handle_SHAKE(self, message):
        key = message.pop('key')
        self.codec.shaked = True  # ***
        self.codec.set_key(key)  # ***
        data = self.codec.encode({"type":"SHAKE"
                                  })
        self.send_data(data)
        
        self.add_inner_glet('cmd_NOP', gevent.spawn_later(1, self.cmd_NOP))
        self.cmd_LOGIN('test', '123456')
        
    def handle_LOGIN(self, message):
        code = message.pop('code')
        if code == 0:
            userid = message.pop('userid')
            logger.info('login: %s', userid)
        else:
            logger.warn('login failed')
        
    def cmd_NOP(self):
        data = self.codec.encode({"type":"NOP"
                                  })
        while 1:
            self.send_data(data)
            gevent.sleep(8)
            
    def cmd_LOGIN(self, username, password):
        data = self.codec.encode({"type":"LOGIN",
                                  "username":username,
                                  "password":password
                                  })
        self.send_data(data)

    def connection_lost(self, reason):
        super(ClientProtocol, self).connection_lost(reason)


class ClientFactory(ReconnectingClientFactory):

    reconnect_delay = 5

    def build_protocol(self, sock, addr):
        logger.info('connection handler %s', str(addr))
        p = ClientProtocol(sock, addr)
        p.factory = self
        return p

cf = ClientFactory(('127.0.0.1', 6011))
cf.start()


gevent.wait()

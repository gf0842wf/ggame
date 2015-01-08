# -*- coding: utf-8 -*-
from gnet.protocol import Protocol, TCPServerFactory
import codec.fixnh
import logging
import ujson as json
import msgpack
import xorcrypt
import zlib
import random
import weakref

from .settings import settings

logger = logging.getLogger(__name__)


class GateServerProtocol(Protocol):
    
    read_deadline = 24  # 心跳超时
    
    # 用户数据
    userid = None
    
    def __str__(self):
        return '[%s:%s]' % (self.userid, str(self.addr))
    
    def __repr__(self):
        return self.__str__()
    
    def connection_made(self):
        # 初始化编解码器
        codec_config = settings['CODEC']
        packet_n = codec_config['packet_n']
        dumps, loads, encrypt, decrypt, compress, decompress = [None] * 6
        
        if codec_config['serialize'] == 'json':
            dumps = json.dumps
            loads = json.loads
        elif codec_config['serialize'] == 'msgpack':
            dumps = msgpack.dumps
            loads = msgpack.loads
            
        self.encrypt_flag = encrypt_flag = codec_config['encrypt_flag']  # 0-不加密(不握手), 1-加密(握手), 2-握手成功, 3-握手失败
        if encrypt_flag:
            encrypt = xorcrypt.encrypt
            decrypt = xorcrypt.decrypt
            self.key = key = random.randint(1, 65535)
            
        if codec_config['compress_flag']:
            compress = zlib.compress
            decompress = zlib.decompress
            
        self.codec = codec.fixnh.Codec(packet_n, '>',
                                       dumps=dumps, loads=loads,
                                       encrypt=encrypt, decrypt=decrypt, key=key,
                                       compress=compress, decompress=decompress,
                                       factory=self
                                       )
        
        # 握手
        if self.encrypt_flag == 1:
            data = self.codec.encode({"type":"SHAKE",
                                      "key":self.key
                                      })
            self.send_data(data)
            self.codec.shaked = True
        
        logger.info('connection made')
        
    def data_received(self, data):
        # TODO: 捕获异常来判断是否握手失败,数据包错误等
        for _, msg in self.codec.decode(data):
            if msg is not None:
                self.message_received(msg)

    def message_received(self, message):
        logger.debug('message: %s', message)
        prefix = message.pop('type')
        if prefix == 'SHAKE':
            pass
        elif prefix == 'LOGIN':
            if self.encrypt_flag != 0:
                if self.encrypt_flag != 2:
                    data = self.codec.encode({"type":"SHAKE",
                                              "code":1
                                              })
                    self.send_lose(data)
                    return
        else:
            if self.userid is None:
                data = self.codec.encode({"type":"LOGIN",
                                          "code":2
                                          })
                self.send_lose(data)
                return
            
        handle = getattr(self, 'handle_%s' % prefix, None)
        if handle:
            handle(message)
        else:
            logger.info('un handle message')
            
    def handle_SHAKE(self, message):
        logger.info('shake ok')
            
    def handle_LOGIN(self, message):
        username = message.pop('username')
        password = message.pop('password')
        if username == 'test' and password == '123456':
            self.userid = userid = 101
            data = self.codec.encode({"type":"LOGIN",
                                      "userid":userid,
                                      "code":0
                                      })
            logger.info('login ok')
            self.send_data(data)
            self.factory.clients[userid] = self
        else:
            data = self.codec.encode({"type":"LOGIN",
                                      "code":2
                                      })
            logger.info('login failed')
            self.send_lose(data)
        
    def handle_NOP(self, message):
        logger.debug('NOP')
    
    def connection_lost(self, reason):
        if self.userid: self.factory.clients.pop(self.userid, None)
        logger.info('connection lost')
        super(GateServerProtocol, self).connection_lost(reason)


class GateServerFactory(TCPServerFactory):
    
    clients = weakref.WeakValueDictionary()
    appid = settings['GATE']['appid']
    appkey = settings['GATE']['appkey']
    addr = None
    
    def __str__(self):
        return '[%s:%s]' % (self.appid, str(self.addr))
    
    def __repr__(self):
        return self.__str__()
    
    def build_protocol(self, sock, addr):
        self.addr = addr
        logger.info('connection handler %s', str(addr))
        p = GateServerProtocol(sock, addr)
        p.factory = self
        return p
    

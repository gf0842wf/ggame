# -*- coding: utf-8 -*-

'''提供了通用的编解码[示例](sock部分使用makefile)
: 如果想实现自己的codec模块 必须实现 Encoder的encode, Decoder的ongoing_decode, EncoderException, DecoderException 等
: 服务器握手、加密、压缩可以在这里实现
'''

import logging
import struct

import gevent

logger = logging.getLogger(__name__)

FMTS = {2:'H', 4:'I', 8:'Q'}
fmt = lambda pachet_n, endian: endian+FMTS[pachet_n]


class EncoderException(Exception):
    pass


class DecoderException(Exception):
    pass


class Encoder(object):
    '''固定nbytes长度头编码器
    
    Example:
    encoder = Encoder(...)
    encoder.encode(...)
    
    '''
    
    def __init__(self, sock, packet_n=4, endian='>', dumps=None):
        self.sock = sock
        self.header_fmt = fmt(packet_n, endian)
        self.dumps = dumps or (lambda data: data)
        
    def encode(self, msg):
        body = self.dumps(msg)
        length = len(body)
        data = struct.pack(self.header_fmt+'%ds' % length, length, body)
        return data


class Decoder(object):
    '''固定nbytes长度头解码器
    
    Example:
    decoder = Decoder(...)
    try:
        for data in decoder.decode(data):
            print data
    except DecoderException:
        ...
    finally:
        ...
        
    '''
        
    def __init__(self, sock, packet_n=4, endian='>', loads=None, header_timeout=None, msg_timeout=None):
        self.sock = sock
        self.sock_file = sock.makefile(mode='r')
        self.packet_n = packet_n
        self.header_fmt = fmt(packet_n, endian)
        self.loads = loads or (lambda data: data)
        self.header_timeout = header_timeout
        self.msg_timeout = msg_timeout
    
    def ongoing_decode(self, on_data):
        '''循环decode数据
        @param on_data: 回调函数, 处理好数据交给 on_data
        '''
        for data in self.decode():
            on_data(data)
                
    def decode(self):
        while True:
            # 读取nbytes头,如果没有读到nbytes会一直阻塞 ,直到超时
            if self.header_timeout is not None:
                with gevent.Timeout(self.header_timeout, DecoderException('header timeout')):
                    header = self.sock_file.read(self.packet_n)
                    if not header: raise DecoderException('not header')
            else:
                header = self.sock_file.read(self.packet_n)
            
            length, = struct.unpack(self.header_fmt, header)
            
            # 读取length bytes消息体,如果没有读到nbytes会一直阻塞 ,直到超时
            if self.msg_timeout is not None:
                with gevent.Timeout(self.msg_timeout, DecoderException('msg timeout')):
                    body = self.sock_file.read(length)
                    if not body: raise DecoderException('not msg')
            else:
                body = self.sock_file.read(length)
                
            msg = self.loads(body)
            yield msg
#             yield ('msg', msg)

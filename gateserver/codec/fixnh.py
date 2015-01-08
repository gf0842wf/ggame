# -*- coding: utf-8 -*-
'''提供了通用的编解码, fix n bytes header
: 服务器握手、加密、压缩可以在这里实现
'''

import logging
import struct

logger = logging.getLogger(__name__)

FMTS = {2:'H', 4:'I', 8:'Q'}
fmt = lambda pachet_n, endian: endian + FMTS[pachet_n]


class CodecException(Exception):
    pass


class Codec(object):
    '''固定nbytes长度头编码器'''
    
    _buf = ''
    
    def __init__(self, packet_n=4, endian='>',
                 dumps=None, loads=None,
                 encrypt=None, decrypt=None, key=None,
                 compress=None, decompress=None,
                 factory=None):
        
        '''不鼓励传递factory,减少耦合
        encode: dumps->encrypt->compress, 这三个传递前请先使用partial设置好默认参数
        decode: decompress->decrypt->loads, 这三个传递前请先使用partial设置好默认参数
        '''
        self.packet_n = packet_n
        self.header_fmt = fmt(packet_n, endian)

        self.dumps = dumps
        self.loads = loads
        
        self.encrypt = encrypt
        self.decrypt = decrypt
        self.key = key
        self.shaked = False
        
        self.compress = compress
        self.decompress = decompress
                   
        self.factory = factory
        
    def set_key(self, key):
        self.key = key
        
    def encode(self, msg):
        body = msg
        if self.dumps:
            body = self.dumps(body)
        if self.encrypt and self.shaked:  # TODO:
            body = self.encrypt(body)
        if self.compress:
            body = self.compress(body)
            
        length = len(body)
        data = struct.pack(self.header_fmt + '%ds' % length, length, body)
        
        return data
    
#     def encode_shake(self, msg):
#         '''握手包编码: 不加密'''
#         body = msg
#         if self.dumps:
#             body = self.dumps(body)
#         if self.compress:
#             body = self.compress(body)
#             
#         length = len(body)
#         data = struct.pack(self.header_fmt + '%ds' % length, length, body)
#         
#         return data
    
    def decode(self, data):
        buf = self._buf = self._buf + data
        packet_n = self.packet_n
        
        while True:
            if not buf:
                raise StopIteration
            
            if len(buf) < packet_n:
                yield ('short_header', None)
                break
            
            length, = struct.unpack(self.header_fmt, buf[:packet_n])
            if len(buf) < length + packet_n:
                yield ('short_msg', None)
                break
            
            body = buf[packet_n:packet_n + length]
            
            buf = buf[packet_n + length:]
            self._buf = buf
            
            msg = body
            if self.decompress:
                msg = self.decompress(msg)
            if self.decrypt and self.shaked:  # TODO: 
                msg = self.decrypt(msg)
            if self.loads:
                msg = self.loads(msg)
            yield ('msg', msg)
            
#     def ongoing_decode(self, on_data):
#         '''循环decode数据
#         @param on_data: 回调函数, 处理好数据交给 on_data
#         '''
#         while True:
#             with gevent.Timeout(self.msg_timeout, DecoderException('msg timeout')):
#                 raw = self.sock.recv(128)
#                 for kind, msg in self.decode(raw):
#                     if kind == 'msg':
#                         body = self.loads(msg)
#                         on_data(body)

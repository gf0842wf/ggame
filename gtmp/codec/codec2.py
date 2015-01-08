# -*- coding: utf-8 -*-

'''提供了通用的编解码[示例]
: 这个没有使用makefile,对比codec,测试效率后再决定使用哪个
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
    '''固定nbytes长度头编码器'''
    
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
    '''固定nbytes长度头解码器'''
        
    _buf = ''
    
    def __init__(self, sock, packet_n=4, endian='>', loads=None, header_timeout=None, msg_timeout=None):
        '''
        @param header_timeout, msg_timeout: 这个Decoder 这两个超时 作用一样,传递一个即可
        '''
        self.sock = sock
        self.packet_n = packet_n
        self.header_fmt = fmt(packet_n, endian)
        self.loads = loads or (lambda data: data)
        self.msg_timeout = msg_timeout or header_timeout
        
    def ongoing_decode(self, on_data):
        '''循环decode数据
        @param on_data: 回调函数, 处理好数据交给 on_data
        '''
        while True:
            with gevent.Timeout(self.msg_timeout, DecoderException('msg timeout')):
                raw = self.sock.recv(128)
                for kind, msg in self.decode(raw):
                    if kind == 'msg':
                        body = self.loads(msg)
                        on_data(body)
            
    def decode(self, data):
        buf = self._buf =  self._buf + data
        packet_n = self.packet_n
        while True:
            if not buf:
                raise StopIteration
            if len(buf) < packet_n:
                yield ('short', 'header')
                break
            length, = struct.unpack(self.header_fmt, buf[:packet_n])
            if len(buf) < length + packet_n:
                yield ('short', 'message')
                break
            body = buf[packet_n:packet_n+length]
            buf = buf[packet_n+length:]
            self._buf = buf
            msg = self.loads(body)
            yield ('msg', msg)

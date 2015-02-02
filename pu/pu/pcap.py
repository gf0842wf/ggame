# -*- coding: utf-8 -*-
from .datatype import pretty_bytes
from .dictutil import DotOrderedDict
import socket
import struct
import sys

stH = struct.Struct('>H')
stI = struct.Struct('>I')

"""''.format_map() in Python 2.x"""
 
try: 
    ''.format_map({})
except AttributeError:  # Python < 3.2
    import string
    def format_map(format_string, mapping, _format=string.Formatter().vformat):
        return _format(format_string, None, mapping)
    del string
  
    # XXX works on CPython 2.6
    # http://stackoverflow.com/questions/2444680/how-do-i-add-my-own-custom-attributes-to-existing-built-in-python-types-like-a/2450942#2450942
    import ctypes as c
  
    class PyObject_HEAD(c.Structure):
        _fields_ = [
            ('HEAD', c.c_ubyte * (object.__basicsize__ - c.sizeof(c.c_void_p))),
            ('ob_type', c.c_void_p)
        ]
  
    _get_dict = c.pythonapi._PyObject_GetDictPtr
    _get_dict.restype = c.POINTER(c.py_object)
    _get_dict.argtypes = [c.py_object]
  
    def get_dict(object):
        return _get_dict(object).contents.value
  
    get_dict(str)['format_map'] = format_map
else:  # Python 3.2+
    def format_map(format_string, mapping):
        return format_string.format_map(mapping)


class Packet(DotOrderedDict):
    def __init__(self):
        DotOrderedDict.__init__(self)

        self.type = self.__class__.__name__


class Ethernet(Packet):
    def __init__(self, ether_type, src, dst, data):
        Packet.__init__(self)

        self.ether_type = ether_type
        self.src = src
        self.dst = dst
        self.data = pretty_bytes(data)

    def __str__(self):
        return '{type} {ether_type:04x} {src} > {dst} {data:hex}'.format_map(self)  # py3


class IP(Packet):
    def __init__(self, sip, dip, proto, data):
        Packet.__init__(self)

        self.proto = proto
        self.sip = sip
        self.dip = dip
        self.data = pretty_bytes(data)

    def __str__(self):
        return '{type} {proto:04x} {sip} > {dip} {data:hex}'.format_map(self)

class ICMP(Packet):
    def __init__(self, sip, dip, data):
        Packet.__init__(self)

        self.sip = sip
        self.dip = dip
        self.data = pretty_bytes(data)

    def __str__(self):
        return '{type} {sip} > {dip} {data:hex}'.format_map(self)
    

class TCP(Packet):
    def __init__(self, sip, sport, dip, dport, flags, seq_no, data):
        Packet.__init__(self)

        self.sip = sip
        self.sport = sport
        self.dip = dip
        self.dport = dport
        self.flags = flags
        self.seq_no = seq_no
        self.data = pretty_bytes(data)

    def __str__(self):
        return '{type} {sip}:{sport} > {dip}:{dport} [{flags}] {seq_no:08x} {data:hex}'.format_map(self)

class UDP(Packet):
    def __init__(self, sip, sport, dip, dport, data):
        Packet.__init__(self)

        self.sip = sip
        self.sport = sport
        self.dip = dip
        self.dport = dport
        self.data = pretty_bytes(data)

    def __str__(self):
        return '{type} {sip}:{sport} > {dip}:{dport} {data:hex}'.format_map(self)

def create_raw_socket(interface=None):
    '''创建 RAW SOCKET
    网络接口:
    - Linux 平台: lo, eth0, eth1, ...
    - Windows 平台: IP 地址
    :param interface: 网络接口
    '''
    if 'linux' in sys.platform:
        s = socket.socket(socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))
        if interface:
            s.bind((interface, 0))
    elif 'win32' in sys.platform:
        # 创建 raw socke
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)

        if not interface:
            # 获取 public network interface
            interface = socket.gethostbyname(socket.gethostname())
        s.bind((interface, 0))

        # 包括 IP 头
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        # 接收所有数据包
        s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    else:
        assert False

    return s


def parse(data):
    '''分析收到的数据
    返回 None, IPPacket, 
    '''
    data_viewer = memoryview(data)

    if 'linux' in sys.platform:
        src = ':'.join('%02x' % ord(b) for b in data_viewer[:6])
        dst = ':'.join('%02x' % ord(b) for b in data_viewer[6:12])
        ether_type, = stH.unpack(data[12:14])
        data_viewer = data_viewer[14:]

        # 只分析 IP 协议
        if ether_type != 0x0800:
            return Ethernet(ether_type, src, dst, data_viewer.tobytes())
    else:
        data_viewer = data_viewer

    ip_header = data_viewer[:20]
    ip_data = data_viewer[20:]

    proto = ord(ip_header[9])
    src_ip = socket.inet_ntoa(ip_header[12:16].tobytes())
    dst_ip = socket.inet_ntoa(ip_header[16:20].tobytes())

    if proto == 1:  # ICMP
        return ICMP(src_ip, dst_ip, ip_data.tobytes())
    elif proto == 6:  # TCP
        tcp_header = ip_data
        data_offset = ord(tcp_header[12]) >> 4
        tcp_data = ip_data[data_offset * 4:]
        src_port, = stH.unpack(tcp_header[0:2].tobytes())
        dst_port, = stH.unpack(tcp_header[2:4].tobytes())
        seq_no, = stI.unpack(tcp_header[4:8].tobytes())

        flags = ord(tcp_header[13])

        flags = ''.join((
            flags & 0x20 and 'U' or '',
            flags & 0x10 and 'A' or '',
            flags & 0x08 and 'P' or '',
            flags & 0x04 and 'R' or '',
            flags & 0x02 and 'S' or '',
            flags & 0x01 and 'F' or '',
            ))

        return TCP(src_ip, src_port, dst_ip, dst_port, flags, seq_no, tcp_data.tobytes())

    elif proto == 17:  # UDP
        udp_header = ip_data
        udp_data = ip_data[8:]

        src_port, = stH.unpack(udp_header[0:2].tobytes())
        dst_port, = stH.unpack(udp_header[2:4].tobytes())

        return UDP(src_ip, src_port, dst_ip, dst_port, udp_data.tobytes())
    else:
        return IP(src_ip, dst_ip, proto, ip_data.tobytes())


def pcap(interface=None):
    s = create_raw_socket(interface)
    while True:
        data, _addr = s.recvfrom(65535)
        packet = parse(data)
        if packet:
            yield packet


if __name__ == '__main__':
    import argparse

    ARGS = argparse.ArgumentParser()

    ARGS.add_argument(
        '--interface', '-i', action='store', dest='interface',
        default=None, help='网络接口(Linux 下 lo, eth0 等, Windows 下是本机IP)')

    ARGS.add_argument(
        '--count', '-n', action='store', dest='count',
        type=int, default=5, help='收到指定数目的数据包后退出.')

    args = ARGS.parse_args()

    count = args.count
    for packet in pcap(args.interface):
        print(packet)
        if count:
            count -= 1
            if not count:
                break

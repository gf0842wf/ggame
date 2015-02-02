# -*- coding: utf-8 -*-
from pu import simplefilter
from pu.pcap import pcap
import argparse


usage = '''
    Windows(注意过滤器两边的双引号):
        pcap.py -i 192.168.6.60 -F "dport=80&&sip=192.168.6.60"
    Linux:
        python pcap.py -i eth0 -F "dport=80&&sip=192.168.6.60"
'''


ARGS = argparse.ArgumentParser(usage=usage, description='截包示例.')

ARGS.add_argument(
    '--interface', '-i', action='store', dest='interface',
    type=str, default=None, help='网络接口(Linux: lo, eth0, ...; Windows: IP 地址).')

ARGS.add_argument(
    '--filter', '-F', action='append', dest='filters',
    type=str, default=[], help='过滤器(如:dport=80&&sip=192.168.6.60)')

args = ARGS.parse_args()


packet_filter = simplefilter.OrFilterGroup()


for f in args.filters:
    packet_filter.parse(f)

print('过滤器:', packet_filter)

for packet in pcap(args.interface):
    if packet_filter(packet):
        print(packet)

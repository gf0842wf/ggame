# -*- coding: utf-8 -*-


class RPCPool(object):
    """分布式rpc池"""
    
    def __init__(self, addrs, mode, rpc_class, *rpc_args, **rpc_kw):
        """
        @param addrs: 所有可连接服务端地址, [(ip, port), ...]
        @param mode: 分布式模式, 0-主从, 1-负载均衡
        """
        self.master_addr = addrs[0]
        self.mode = mode
        
        self.master_rpcs = rpc_class(self.master_addr, *rpc_args, **rpc_kw)
        self.slave_rpcs = {addr:rpc_class(addr, *rpc_args, **rpc_kw) for addr in addrs[1:]}
        
        self._rpc_class = rpc_class
        self._rpc_args = rpc_args
        self._rpc_kw = rpc_kw
        
    def call(self, method, *args):
        pass
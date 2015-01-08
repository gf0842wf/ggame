# 分布式RPC

采用 [`mprpc`](https://github.com/gf0842wf/mprpc "mprpc")  

优点

- 速度快
- 通用, 可以用其他语言来优化

协议

`msgpack rpc`

结构

- 采用主从结构, 主节点请求失败则会请求从节点 <容灾>
- 采用均衡结构, 所有节点均衡接受请求 <负载>

配置

- 采用json文件

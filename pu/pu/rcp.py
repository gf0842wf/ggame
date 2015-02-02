# -*- coding: utf-8 -*-
'''Remote Call Protocol

远程过程调用协议，参考 JSON-RPC 定义，但针对 Python 语言特点做了如下改变:

- 简化: 保留必要的字段，用列表取代字典
- 明确: 明确定义了各种消息的格式

本协议的目标是提供一个最小的消息集合，至于扩展性等问题，可以通过上层协议进行处理。

四种消息类型:

Notify
------

通知消息，不需要对方回应，格式::

    ['N', 'method', args, kwargs]

- method:   字符串，方法名
- args:     列表或 tuple
- kwargs:   字典

Call
----

远程调用，对方返回 Return 或 Error 消息，格式::

    ['C', id, 'method', args, kwargs]

- id:       调用标识
- method:   方法名
- args:     列表或 tuple
- kwargs:   字典

Return
------

对 Call 的成功响应，格式::

    ['R', id, result]

- id:       对应 Call 中的 id
- result:   返回结果

Error
-----

错误响应， 格式::

    ['E', id, code, reason, data]

- id:       对应 Call 中的 id
- code:     错误代码
- reason:   错误描述
- data:     附加数据


常见错误代码::

- 101:      协议解析错误
- 102:      方法不存在
- 103:      参数错误
- 104:      内部错误
- 105~199:  其他错误


参考:

- http://en.wikipedia.org/wiki/JSON-RPC
- http://www.jsonrpc.org/specification
'''
from collections import namedtuple


__all__ = ['Notify', 'Call', 'Return', 'Error', 'decode', 'encode']


NOTIFY = 'N'
CALL = 'C'
RETURN = 'R'
ERROR = 'E'


class EncodeError(Exception):
    pass


class DecodeError(Exception):
    pass


Notify = namedtuple('Notify', ['method', 'args', 'kwargs'])
Call = namedtuple('Call', ['id', 'method', 'args', 'kwargs'])
Return = namedtuple('Return', ['id', 'result'])
Error = namedtuple('Error', ['id', 'code', 'reason', 'data'])


def decode(lst):
    message_type, args = lst

    if message_type == NOTIFY:
        message = Notify(*args)
    elif message_type == CALL:
        message = Call(*args)
    elif message_type == RETURN:
        message = Return(*args)
    elif message_type == ERROR:
        message = Error(*args)
    else:
        raise DecodeError('decode error: %r' % lst)

    return message


def encode(message):
    if isinstance(message, Notify):
        lst = [NOTIFY]
    elif isinstance(message, Call):
        lst = [CALL]
    elif isinstance(message, Return):
        lst = [RETURN]
    elif isinstance(message, Error):
        lst = [ERROR]
    else:
        raise EncodeError('encode error: %r' % message)

    lst.extend(message)

    return lst

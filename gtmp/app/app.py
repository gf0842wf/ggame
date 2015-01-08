# -*- coding: utf-8 -*-

'''bottle的app, 提供一个支持websocket示例'''

import logging

import bottle

from bottle.ext.websocket import websocket

logger = logging.getLogger(__name__)

app = bottle.Bottle()

@app.route('/', method='GET')
def index():
    return 'hello, world!'

@app.route('/ws', apply=[websocket], method='GET')
def echo(ws):
    while True:
        msg = ws.receive()
        if msg: ws.send()

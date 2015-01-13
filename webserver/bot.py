# -*- coding: utf-8 -*-
'''模拟http和websocket请求的,测试(压测)工具'''

from gevent import monkey; monkey.patch_all()
from websocket import create_connection
import requests
import gevent
import sys

try:
    username, password = sys.argv[1:3]
except:
    print 'argv error'
    sys.exit()

# 登陆 获取cookie
r = requests.post('http://127.0.0.1:6001/api/v1/game/login',
                  data={'username':username, 'password':password, 'byapi':1}
                  )

cookie = 'Cookie: p=%s; u=%s' % (r.cookies['p'], r.cookies['u'])
print 'cookie:', cookie

options = {'cookie': cookie}

# 拿cookie连接websocket
ws = create_connection("ws://127.0.0.1:6001/api/v1/game/ws/check", **options)
while True:
    msg = ws.recv()
    if not msg:
        break
    print msg

ws.close()

print 'enter game, close websocket'

gevent.wait()

# usage: 
# python bot.py 111 111
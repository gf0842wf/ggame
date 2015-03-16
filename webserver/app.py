# -*- coding: utf-8 -*-
from bottle.ext.websocket import websocket
# from bottle import redirect, request, response, static_file
import bottle
import logging
import os
import random
import time
import ujson as json
from bson import ObjectId
from functools import wraps

from pu.util import shorten
from .settings import settings
from ._path import HOME_DIR
from .dblpc import monlpc

from gnet.client import Client

mondb = Client()['mongo_client']

logger = logging.getLogger(__name__)

bottle.debug(True)

app = bottle.Bottle()

now_date = lambda: time.strftime("%Y-%m-%d %X")
now = lambda: int(time.time())


# authorize 装饰器
def authorize(db):
    def _wrapper(fn):
        @wraps(fn)
        def __wrapper(*args, **kw):
            secret = settings['API']['secret']
            uid = bottle.request.get_cookie('u', secret=secret)
            password = bottle.request.get_cookie('p', secret=secret)
            if not uid or not password:
                return json.dumps({'code': 1, 'msg': 'username&password error or auth expire'})
            user = db.user.find_one({'_id': ObjectId(uid), 'password': password}, {'_id': 1})
            if not user:
                bottle.response.delete_cookie("u", path='/')
                bottle.response.delete_cookie("p", path='/')
                return json.dumps({'code': 1, 'msg': 'username&password error or auth expire'})
                # return bottle.redirect('/api/v1/game/login')
            return fn(*args, **kw)

        return __wrapper

    return _wrapper


def get_user():
    secret = settings['API']['secret']
    uid = bottle.request.get_cookie('u', secret=secret)
    password = bottle.request.get_cookie('p', secret=secret)
    return {'_id': ObjectId(uid), 'password': password}


@app.error(400)
def error400(error):
    return json.dumps({'code': 400, 'msg': 'http syntax error'})


@app.error(404)
def error404(error):
    return json.dumps({'code': 404, 'msg': 'page not found'})


@app.error(405)
def error405(error):
    return json.dumps({'code': 405, 'msg': 'auth error'})


@app.error(500)
def error500(error):
    return json.dumps({'code': 500, 'msg': 'internal server error'})


@app.route('/', method='GET')
@authorize(mondb)
def index():
    return 'hello, world!'


@app.route('/ws', apply=[websocket], method='GET')
def echo(ws):
    if not ws:
        logger.warn('not websocket connection')
        return

    logger.info('websocket connection made')

    try:
        while True:
            msg = ws.receive()
            if msg:
                logger.debug('ws msg: %s', shorten(msg, 32))
                ws.send(msg)
            else:
                logger.info('websocket not msg')
                break
        logger.info('websocket connection lost')
        ws.close()
    except:
        logger.warn('websocket connection lost except', exc_info=1)


@app.route('/api/v1/game/register', method='POST')
def register():
    bottle.response.set_header('Content-Type', 'application/json; charset=UTF-8')
    req = bottle.request.json
    username = req['username']
    password = req['password']
    auth_code = req['auth_code']
    nickname = req['nickname']

    exist = mondb.user.find_one({'username': username, 'password': password})
    if exist:
        return json.dumps({'code': 2, 'msg': 'the username has exists'})

    try:
        options = {'username': username, 'password': password, 'nickname': nickname, 'create_date': now_date()}
        oid = mondb.user.insert(options)
    except:
        # TODO: rollback
        logger.error('register user error: %s', username, exc_info=1)
        return json.dumps({'code': 99, 'msg': 'unknown error'})

    uid = str(oid)
    return json.dumps({'code': 0, 'uid': uid})


@app.route('/api/v1/game/login', method='POST')
def login():
    bottle.response.set_header('Content-Type', 'application/json; charset=UTF-8')
    req = bottle.request.json  # json.loads(bottle.request.body.getvalue())
    username = req['username']
    password = req['password']
    user = mondb.user.find_and_modify(query={"username": username, "password": password},
                                      update={"$set": {"login_date": now_date()}},
                                      new=False,
                                      fields={'_id': 1})

    secret = settings['API']['secret']

    if not user:
        bottle.response.delete_cookie("u", path='/')
        bottle.response.delete_cookie("p", path='/')
        return json.dumps({'code': 1, 'msg': 'username&password error or auth expires'})

    uid = str(user['_id'])
    bottle.response.set_cookie('u', uid, secret=secret, path='/', max_age=3600 * 24 * 5)
    bottle.response.set_cookie('p', password, secret=secret, path='/', max_age=3600 * 24 * 5)
    return json.dumps({'code': 0, 'uid': uid})


@app.route('/api/v1/game/logout', method='POST')
def logout():
    bottle.response.set_header('Content-Type', 'application/json; charset=UTF-8')
    bottle.response.delete_cookie('u', path='/')
    bottle.response.delete_cookie('p', path='/')
    return json.dumps({'code': 0})


@app.route('/api/v1/game/fitting', method='GET')
@authorize(mondb)
def fitting():
    bottle.response.set_header('Content-Type', 'application/json; charset=UTF-8')
    _user = get_user()
    # _user.update({'backpack.wearing':1})
    user = mondb.user.find_one(_user, {'backpack.id': 1, 'backpack.type': 1, 'backpack.wearing': 1})
    backpack = user['backpack']
    user['wearing'] = []
    user['backpack'] = []
    for d in backpack:
        wearing = d['wearing']
        if wearing == 1:
            user['wearing'].append({'id': d['id'], 'type': d['type']})
        elif wearing == 0:
            user['backpack'].append({'id': d['id'], 'type': d['type']})
    user['code'] = 0
    user.pop('_id')

    return json.dumps(user)


@app.route('/api/v1/game/upload/image', method='GET')
@authorize(mondb)
def get_upload_image():
    html = '''\
    <html xmlns='http://www.w3.org/1999/xhtml'> 
    <head> 
    <meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/> 
    <title>Image Upload</title>
    </head>
    <body>
    <p><h1>Image Upload</h1></p>
    <form enctype='multipart/form-data' action='/api/game/upload/image' method='post'>
    File: <input type='file' name='name' />
    <br />
    <br />
    <input type='submit' value='upload' />
    </form>
    '''
    return html


@app.route('/api/v1/game/upload/image', method='POST')
@authorize(mondb)
def post_upload_image():
    bottle.response.set_header('Content-Type', 'application/json; charset=UTF-8')
    upfile = bottle.request.files.get('name')
    if upfile:
        suffix = 'static/img/%s' % upfile.filename
        p = os.path.join(HOME_DIR, suffix)
        upfile.save(p, overwrite=True)
    else:
        return json.dumps({'code': 1, 'msg': 'not file'})
    md5 = str(random.randint(0, 10000))
    return json.dumps({'code': 0, 'md5': md5, 'image': settings['API']['root'] + suffix, 'thumb': ''})


@app.route('/static/img/<filename>', method='GET')
# @authorize(mondb)
def serve_img(filename):
    p = os.path.join(HOME_DIR, 'static/img')
    return bottle.static_file(filename, root=p)

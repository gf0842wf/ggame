# -*- coding: utf-8 -*-
from _path import init_path; init_path()
from gevent import monkey; monkey.patch_all()
import argparse
import gevent
import os
import logging

from settings import settings
from _path import HOME_DIR


# 分析参数
ARGS = argparse.ArgumentParser(description='rpc server')

ARGS.add_argument(
    '--port', '-p', action='store', dest='port',
    default=6021, type=int, help='server port to listen on.')

ARGS.add_argument(
    '--logfile', '-l', action='store', dest='logfile',
    default='-', type=str, help="logfile, '-' means stdout.")

ARGS.add_argument(
    '--loglevel', '-L', action='store', dest='loglevel',
    default='INFO', type=str, help='log level(DEBUG, INFO, WARN, ERROR).')

ARGS.add_argument(
    '--settings', '-s', action='store', dest='settings',
    default='etc/rpc/default.json', type=str, help='setting file.')

ARGS = ARGS.parse_args()


def initialize():
    # 加载配置文件
    settings.load(os.path.join(HOME_DIR, ARGS.settings))

    loglevel = logging._checkLevel(ARGS.loglevel)

    # 日志配置
    log_format = '[%(asctime)-15s %(levelname)s:%(name)s:%(module)s] %(message)s'
    logging.basicConfig(level=loglevel, format=log_format)


def run():
    # 先启动(导入)client,后启动service
    from gateserver.client import client

    client.start()
    from rpcserver.service import root

    root.start()


def main():
    initialize()
    run()


main()

gevent.wait()

# python rpcserver --loglevel DEBUG --settings etc/rpc/default.json

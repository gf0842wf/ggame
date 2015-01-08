# -*- coding: utf-8 -*-
from path import init_path;init_path()
import sys; sys.modules.pop('threading', None)
from gevent import monkey; monkey.patch_all()
# 注意上面两句的顺序,不能反过来,这两句只能在引导文件开头出现,其它地方不需要加了

import argparse
import gevent
import os
import logging

from webserver.settings import settings
from webserver.path import HOME_DIR

# 分析参数
ARGS = argparse.ArgumentParser(description='web server')

# ARGS.add_argument(
#     '--port', '-p', action='store', dest='port',
#     default=6001, type=int, help='server port to listen on.')

ARGS.add_argument(
    '--logfile', '-l', action='store', dest='logfile',
    default='-', type=str, help="logfile, '-' means stdout.")

ARGS.add_argument(
    '--loglevel', '-L', action='store', dest='loglevel',
    default='DEBUG', type=str, help='log level(DEBUG, INFO, WARN, ERROR).')

ARGS.add_argument(
    '--settings', '-s', action='store', dest='settings',
    default='etc/web/default.json', type=str, help='setting file.')

ARGS = ARGS.parse_args()

def initialize():
    # 加载配置文件
    settings.load(os.path.join(HOME_DIR, ARGS.settings))
    
    loglevel = logging._checkLevel(ARGS.loglevel)
    
    # 日志配置
    log_format = '[%(asctime)-15s %(levelname)s:%(name)s:%(module)s] %(message)s'
    logging.basicConfig(level=loglevel, format=log_format)

def run():
    # 在load配置文件后才能导入root
    # 先启动(导入)client,后启动service
    from webserver.client import client
    client.start()
    from webserver.service import service
    service.start()
    
def main():
    initialize()
    run()

main()

gevent.wait()

# python webserver --loglevel DEBUG --settings etc/web/default.json

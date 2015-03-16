# -*- coding: utf-8 -*-
"""db local process call
: 把db操作全都封装为函数,不在其他地方出现sql语句
: 暂时不打算使用orm (以后会考虑ponyorm)
"""

from gnet.client import Client  # Client是单例模式, 在__main__中已经初始化了
import logging

logger = logging.getLogger(__name__)

client = Client()


class DBLPC(object):
    """写封装sql的方法
    : TODO: 加redis缓存/内存缓存
    """

    def __init__(self, db):
        self._client = db

    def now_date(self):
        """返回mysql系统时间
        @return: mysql的日期时间串(对应python datetime类型)
        """
        return self._client.fetchone('select now() as now_date')['now_date']

    def now(self):
        """返回mysql系统时间
        @return: mysql的unix时间戳
        """
        return self._client.fetchone('select unix_timestamp() as now')['now']


mylpc = DBLPC(client['mysql_client'])

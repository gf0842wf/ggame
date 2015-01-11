# -*- coding: utf-8 -*-
'''db local process call
: 把db操作全都封装为函数,不在其他地方出现sql语句
: 暂时不打算使用orm (以后会考虑gevent+ponyorm+pymysql)
'''
from gnet.client import Client  # Client是单例模式, 在__main__中已经初始化了
import logging

logger = logging.getLogger(__name__)

client = Client()


class MyDBLPC(object):
    '''写封装sql的方法
    : TODO: 加redis缓存/内存缓存
    : TODO: 把事务封装成装饰器
    : TODO: 封装出一个user,活跃user常驻内存(或redis),以user为主体设计方法
    '''
    
    def __init__(self, db):
        self._db = db
        
    def now_date(self):
        '''返回mysql系统时间
        @return: mysql的日期时间串(对应python datetime类型)
        '''
        return self._db.fetchone('select now() as now_date')['now_date']
    
    def now(self):
        '''返回mysql系统时间
        @return: mysql的unix时间戳
        '''
        return self._db.fetchone('select unix_timestamp() as now')['now']
    
    def get_user(self, where, fields='*'):
        ''' 通过where获得1个 user
        @param where: where条件串  eg. "uid='fk' and password='1234'" 
        @param fields: 返回的字段串 eg. "id as uid, username"   "*"
        @return: user字典
        '''
        sql = 'select %s from user where %s' % (fields, where)
        if 'None' in sql: return  # 这里设定where语句里面不能有None
        return self._db.fetchone(sql)
    
    def upsert_user(self, options):
        ''' 更新插入用户(不存在就插入)
        @param options: 键值字典 eg. {'username':'', 'password':'', 'nickname':'', 'create_date':''}
        '''
        ks = options.keys()
        vs = [unicode(options[k]).encode('utf-8') for k in ks]
        fields = ','.join(ks)
        values = ','.join(map(lambda v: '"%s"' % v, vs))
        cross = ','.join(map(lambda kv:'%s="%s"' % kv, zip(ks, vs)))
        sql = 'insert into user ' + ' (%s) ' % fields + 'values' + ' (%s) ' % values + ' on duplicate key update ' + cross
#         sql = 'insert into user (username, password, nickname, create_date) values ("%s", "%s", "%s", "%s") on duplicate key update username="%s", password="%s", nickname="%s", create_date="%s"'
        return self._db.execute(sql) 
    
    def test_transaction(self):
        '''测试事务
        q.put(1)
        q.put(2)
        q.put(3)
        :只要中间没有sleep啥的就是原子的
        :使用事务时必须指定 qid
        '''
        self._db.execute('START TRANSACTION', qid=0)
        self._db.query('SET AUTOCOMMIT=0', qid=0)
        self._db.query('insert into user (username, password, nickname) values ("fk", 1123, "a")', qid=0)
        self._db.execute('ROLLBACK')
        self._db.execute('COMMIT', qid=0)
        self._db.query('SET AUTOCOMMIT=1', qid=0)
        
        
class MonDBLPC(object):
    '''写封装mongodb的方法,仅限于复杂的方法,简单操作可以直接用mongo_client操作
    : TODO: 用日志代替事务
    '''
    
    def __init__(self, db):
        self._db = db
        

# mylpc = MyDBLPC(client['mysql_client'])
monlpc = MonDBLPC(client['mongo_client'])

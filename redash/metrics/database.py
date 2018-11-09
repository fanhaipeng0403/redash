"""
数据库查询耗时设置
以及使用statsD记录在整个项目周期

"""
import logging
import time


####请求和应用上下文
from flask import g, has_request_context

# https://www.cnblogs.com/yasmi/p/5056089.html
# http://www.xby1993.net/pages/dokuwiki/python/sqlalchemy.html
# https://docs.sqlalchemy.org/en/latest/core/event.html?highlight=listen#sqlalchemy.event.listen

####记录工具
from redash import statsd_client


######数据库监听

from sqlalchemy.engine import Engine
from sqlalchemy.event import listens_for
from sqlalchemy.orm.util import _ORMJoin
from sqlalchemy.sql.selectable import Alias

metrics_logger = logging.getLogger("metrics")


def _table_name_from_select_element(elt):
    t = elt.froms[0]

    if isinstance(t, Alias):
        t = t.original.froms[0]

    while isinstance(t, _ORMJoin):
        t = t.left

    return t.name


## 装饰器
@listens_for(Engine, "before_execute")

# 调用了这个方法
# listen(target, identifier, fn, *args, **kw)
# listen(Engine, ,before_execute,  'before_execute')

def before_execute(conn, elt, multiparams, params):
    # setdefault
    # 有key存在，就返回key对应的值,
    # 没有,就设置key和对应的值

    # time.time() 时间戳
    conn.info.setdefault('query_start_time', []).append(time.time())


@listens_for(Engine, "after_execute")
def after_execute(conn, elt, multiparams, params, result):
    # pop 移除指定index的元素
    # remove 移除指元素中第一个
    duration = 1000 * (time.time() - conn.info['query_start_time'].pop(-1))
    action = elt.__class__.__name__

    if action == 'Select':
        name = 'unknown'
        try:
            name = _table_name_from_select_element(elt)
        except Exception:
            logging.exception('Failed finding table name.')
    elif action in ['Update', 'Insert', 'Delete']:
        name = elt.table.name
    else:
        # create/drop tables, sqlalchemy internal schema queries, etc
        return

    action = action.lower()

    # 对某个表的，执行了的什么操作（select,update等），消耗多长时间
    statsd_client.timing('db.{}.{}'.format(name, action), duration)
    # 日志记录
    metrics_logger.debug("table=%s query=%s duration=%.2f", name, action,
                         duration)

    if has_request_context():

        # current_app、g就是应用上下文, 线程成内的全局变量
        # requests、session就是请求上下文
        # request 封装了client发出的http请求内容
        # session 储存了用户请求之间的需要记住的值字典


        # 源码你就会发现 session 也是一个 request context 的变量，但它把数据保存到了 cookie 中并发送到了客户端，客户端再次请求的时候又带上了cookie。
        g.setdefault('queries_count', 0)
        g.setdefault('queries_duration', 0)



        g.queries_count += 1
        g.queries_duration += duration

    return result
# https://blog.tonyseek.com/post/the-context-mechanism-of-flask/
# https://www.zhihu.com/question/33970027

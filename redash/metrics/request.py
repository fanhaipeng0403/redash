import logging
import time
from collections import namedtuple

from flask import g, request
from redash import statsd_client

metrics_logger = logging.getLogger("metrics")


def record_requets_start_time():
    # 在每个请求之前，执行 before_request() 上绑定的函数。 如果这些函数中的某个返回了一个响应，其它的函数将不再被调用。
    # 任何情况下，无论如何这个返回值都会替换视图的返回值。

    # 如果 before_request() 上绑定的函数没有返回一个响应， 常规的请求处理将会生效，匹配的视图函数有机会返回一个响应。

    g.start_time = time.time()


def calculate_metrics(response):
    # 视图的返回值之后会被转换成一个实际的响应对象，并交给 #after_request() # 上绑定的函数适当地替换或修改它。
    if 'start_time' not in g:
        ####返还给客户端
        return response

    ####计算整个请求消耗时间########
    request_duration = (time.time() - g.start_time) * 1000

    ####计算此次请求的数据库消耗时间以及频率########

    # D:\redash - master\redash\metrics\database.py
    # if has_request_context():
    #     g.setdefault('queries_count', 0)
    #     g.setdefault('queries_duration', 0)
    #     g.queries_count += 1
    #     g.queries_duration += duration

    queries_duration = g.get('queries_duration', 0.0)
    queries_count = g.get('queries_count', 0.0)

    ###########记录请求资源##############
    endpoint = (request.endpoint or 'unknown').replace('.', '_')

    ###########记录到日志里#############
    metrics_logger.info(
        "method=%s path=%s endpoint=%s status=%d content_type=%s content_length=%d duration=%.2f query_count=%d query_duration=%.2f",
        request.method,
        request.path,
        endpoint,
        response.status_code,
        response.content_type,
        response.content_length or -1,
        request_duration,
        queries_count,
        queries_duration)

    ####### 利用statsd可以记录request和time的关系，制作一个时间流的图形
    ####### statsd可以采集指标，指标就是随时间变化度量的值
    ###### 事实上，logging也可以通过time和记录，通过grep统计出来，但是太麻烦了？？？？？
    statsd_client.timing('requests.{}.{}'.format(endpoint, request.method.lower()), request_duration)

    ####返还给客户端
    return response


####伪造一个请求
# MockResponse = namedtuple('MockResponse', ['status_code', 'content_type', 'content_length'])
# 之所以使用，nametuple命名元组，是为了 response = MockResponse(500, '?', -1),  response.status_code可在calculate_metrics中兼容


def calculate_metrics_on_exception(error):
    if error is not None:
        ##### 错误发生时，可能都还没产生reponse
        ####  我们模拟一个response
        ####  达到统计测量的目的
        calculate_metrics(MockResponse(500, '?', -1))


def provision_app(app):
    #### 接收到请求时，计时开始,放入全局变量g中################
    app.before_request(record_requets_start_time)

    #### 完成到请求时， 结束计时,统计请求次数，消耗时间，以及数据库消耗，发送个statsD和日志################
    app.after_request(calculate_metrics)

    # 在请求的最后，会执行 teardown_request() 上绑定的函数
    # 注意销毁回调总是会被执行，即使没有请求前回调执行过，或是异常发生。类似于finally
    #
    app.teardown_request(calculate_metrics_on_exception)

import logging
import time

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

# https://www.jianshu.com/p/7a7efbb7205f

# Flask中有四种请求hook，分别是@before_first_request @before_request @after_request @teardown_request
# 除了request的请求上下文
# 还存在应用上下文，current_app


# 既然在 Web 应用运行时里，应用上下文 和 请求上下文 都是 Thread Local 的，那么为什么还要独立二者？
# 查阅资料后发现第一个问题是因为设计初衷是为了能让两个以上的Flask应用共存在一个WSGI应用中，这样在请求中，需要通过应用上下文来获取当前请求的应用信息。


# app context 是从 request context 中分离出来的，在 flask 0.7 以前只有 request context 没有 app context。之所以把 app context
# 分离出来是因为有时只需要 app context （比如离线脚本）这时如果还要创建 request context 就会比较浪费资源以及时间。所以提供单独创建 app context 的功能。
# 但是在实际的程序运行状态（app 的三种状态之一）
# app context 和 request context 的生命周期是一样的：在请求开始时创建，在请求结束时销毁
# 而 app context 却有点误导性，它的字面意思是 应用上下文，但它不是一直存在的，它只是request context 中的一个对 app 的代理(人)，
# 所谓local proxy。它的作用主要是帮助 request 获取当前的应用，它是伴 request 而生，随 request 而灭的


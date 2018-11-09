# print 到chrome的console里
# https://glasslion.github.io/zha-beta/post/57590624308/chrome-logger/

import time

import chromelogger as console
from flask import g, request
from flask_sqlalchemy import get_debug_queries

# >>> from my_app import User
# >>> from flask_sqlalchemy import get_debug_queries
# >>> User.query.filter_by(display_name='davidism').all()
# >>> info = get_debug_queries()[0]
# >>> print(info.statement, info.parameters, info.duration, sep='\n')
#
# SELECT "user".id AS user_id, se_user.id AS se_user_id, se_user.display_name AS se_user_display_name, se_user.profile_image AS se_user_profile_image,
# se_user.profile_link AS se_user_profile_link, se_user.reputation AS se_user_reputation, "user".superuser AS user_superuser \nFROM se_user JOIN "user"
# ON se_user.id = "user".id \nWHERE se_user.display_name = %(display_name_1)s
#
# {'display_name_1': 'davidism'}
#
# 0.0016849040985107422

def log_queries():
    total_duration = 0.0
    queries_count = 0

    # 开始
    console.group("SQL Queries")
    ######################################################################

    # 记录此次请求，
    # 执行了几次sql，总共花了多长的执行时间，以及每次查询的内容，参数和时间

    for q in get_debug_queries():
        # 每次查询的内容，参数和时间
        total_duration += q.duration
        queries_count += 1
        console.info(q.statement % q.parameters)
        console.info("Runtime: {:.2f}ms".format(1000 * q.duration))

    # 执行了几次sql，总共花了多长的执行时间，
    console.info("{} queries executed in {:.2f}ms.".format(queries_count, total_duration * 1000))

    ######################################################################
    console.group_end("SQL Queries")
    # 结束


def chrome_log(response):

    request_duration = (time.time() - g.start_time) * 1000

    # g程序上下文，存在于一次请求的处理的生命周期里
    # database的监听器，每次查询都会记录进g
    # 下次请求g，重置


    # D:\redash - master\redash\metrics\database.py

    #         g.setdefault('queries_count', 0)
    #         g.setdefault('queries_duration', 0)
    #         g.queries_count += 1
    #         g.queries_duration += duration
    queries_duration = g.get('queries_duration', 0.0)
    queries_count = g.get('queries_count', 0)

    #  记录整个请求的时间
    # get /resource  （200，  100.10ms runtime， 5 queries in 50ms）

    group_name = '{} {} ({}, {:.2f}ms runtime, {} queries in {:.2f}ms)'.format(
        request.method, request.path, response.status_code, request_duration, queries_count, queries_duration)
    # 开始
    console.group_collapsed(group_name)
    ######################################################################

    endpoint = (request.endpoint or 'unknown').replace('.', '_')
    console.info('Endpoint: {}'.format(endpoint))
    console.info('Content Type: {}'.format(response.content_type))
    console.info('Content Length: {}'.format(response.content_length or -1))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    log_queries()


    console.group_end(group_name)

    # 结束
    ######################################################################

    header = console.get_header()
    if header is not None:
        response.headers.add(*header)

    return response


def init_app(app):
    if not app.debug:
        return

    app.after_request(chrome_log)

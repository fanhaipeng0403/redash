# print 到chrome的console里

import time
import console as console
from flask import g, request
from flask_sqlalchemy import get_debug_queries


def log_queries():
    total_duration = 0.0
    queries_count = 0

    console.group("SQL Queries")

    for q in get_debug_queries():
        total_duration += q.duration
        queries_count += 1
        console.info(q.statement % q.parameters)
        console.info("Runtime: {:.2f}ms".format(1000 * q.duration))

    console.info("{} queries executed in {:.2f}ms.".format(queries_count, total_duration*1000))

    console.group_end("SQL Queries")


def chrome_log(response):
    request_duration = (time.time() - g.start_time) * 1000
    queries_duration = g.get('queries_duration', 0.0)
    queries_count = g.get('queries_count', 0)

    ### print 分组开始
    group_name = '{} {} ({}, {:.2f}ms runtime, {} queries in {:.2f}ms)'.format(
        request.method, request.path, response.status_code, request_duration, queries_count, queries_duration)

    console.group_collapsed(group_name)
    
    endpoint = (request.endpoint or 'unknown').replace('.', '_')

    console.info('Endpoint: {}'.format(endpoint))
    console.info('Content Type: {}'.format(response.content_type))
    console.info('Content Length: {}'.format(response.content_length or -1))

    log_queries()

    console.group_end(group_name)
    ### print 分组结束

    header = console.get_header()
    if header is not None:
        response.headers.add(*header)

    return response


def init_app(app):
    if not app.debug:
        return 

    app.after_request(chrome_log)

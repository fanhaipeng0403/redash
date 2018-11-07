from __future__ import absolute_import

import logging
import time

import pystache
from flask import request
from flask_login import current_user, login_required
from flask_restful import abort
from redash import models, utils
from redash.handlers import routes
from redash.handlers.base import (get_object_or_404, org_scoped_rule,
                                  record_event)
from redash.handlers.query_results import collect_query_parameters
from redash.handlers.static import render_index
from redash.utils import gen_query_hash

from .authentication import current_org


#
# Run a parameterized query synchronously and return the result
# DISCLAIMER: Temporary solution to support parameters in queries. Should be
#             removed once we refactor the query results API endpoints and handling
#             on the client side. Please don't reuse in other API handlers.
#
def run_query_sync(data_source, parameter_values, query_text, max_age=0):
    query_parameters = set(collect_query_parameters(query_text))
    missing_params = set(query_parameters) - set(parameter_values.keys())
    if missing_params:
        raise Exception('Missing parameter value for: {}'.format(", ".join(missing_params)))

    if query_parameters:
        query_text = pystache.render(query_text, parameter_values)

    if max_age <= 0:
        query_result = None
    else:
        query_result = models.QueryResult.get_latest(data_source, query_text, max_age)

    query_hash = gen_query_hash(query_text)

    if query_result:
        logging.info("Returning cached result for query %s" % query_hash)
        return query_result.data

    try:
        started_at = time.time()
        data, error = data_source.query_runner.run_query(query_text, current_user)

        if error:
            return None
        # update cache
        if max_age > 0:
            run_time = time.time() - started_at
            query_result, updated_query_ids = models.QueryResult.store_result(data_source.org_id, data_source.id,
                                                                              query_hash, query_text, data,
                                                                              run_time, utils.utcnow())

            models.db.session.commit()
        return data
    except Exception:
        if max_age > 0:
            abort(404, message="Unable to get result from the database, and no cached query result found.")
        else:
            abort(503, message="Unable to get result from the database.")
        return None


######## url的参数规范：

# ?后面加参数， mode=job ， 不同参数与之间使用&，action=update&jobid=1
# http://127.0.0.1:888/api?model=job&action=update&jobid=1

######## flask的url特色

# /user/<username>'
# /post/<int:post_id>

#######例子

# >>> from flask import Flask, url_for
# >>> app = Flask(__name__)
# >>> @app.route('/')
# ... def index(): pass
# ...
# >>> @app.route('/login')
# ... def login(): pass
# ...
# >>> @app.route('/user/<username>')
# ... def profile(username): pass
# ...
# >>> with app.test_request_context():
# ...  print url_for('index')
# ...  print url_for('login')
# ...  print url_for('login', next='/')
# ...  print url_for('profile', username='John Doe', job='teacher')
# ...
# /
# /login
# /login?next=/
# /user/John%20Doe?job=teacher        （内填充进flask的<>参数里，就 填充，不能则使用标准的url规范）

# org_scoped_rule, 组织域规则
@routes.route(org_scoped_rule('/embed/query/<query_id>/visualization/<visualization_id>'), methods=['GET'])
# /<org_slug:org_slug>/embed/query/<query_id>/visualization/<visualization_id>
# 或
# /embed/query/<query_id>/visualization/<visualization_id>

@login_required
def embed(query_id, visualization_id, org_slug=None):
    # record_event
    # 所有的请求相关信息都会被记录

    # id   org_id user_id   action              object_type   created_at
    # 1     1       1        login           personal_homepage   05/10/18:11:50

    # object_id additional_properties

    # {"ip": "13.124.223.158",
    #  "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"}

    record_event(current_org, current_user._get_current_object(), {
        'action': 'view',
        'object_id': visualization_id,
        'object_type': 'visualization',
        'query_id': query_id,
        'embed': True,
        'referer': request.headers.get('Referer')
    })

    return render_index()


@routes.route(org_scoped_rule('/public/dashboards/<token>'), methods=['GET'])
@login_required
def public_dashboard(token, org_slug=None):
    if current_user.is_api_user():
        dashboard = current_user.object
    else:
        api_key = get_object_or_404(models.ApiKey.get_by_api_key, token)
        dashboard = api_key.object

    record_event(current_org, current_user, {
        'action': 'view',
        'object_id': dashboard.id,
        'object_type': 'dashboard',
        'public': True,
        'headless': 'embed' in request.args,
        'referer': request.headers.get('Referer')
    })
    return render_index()

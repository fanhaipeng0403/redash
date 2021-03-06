#########################
# 这个模块放置,所有,基础的,通用的部件，给handler包内的其他文件使用


import time
from inspect import isclass

from flask import Blueprint, current_app, request
from flask_login import current_user, login_required
from flask_restful import Resource, abort
from redash import settings
from redash.authentication import current_org
from redash.models import db
from redash.tasks import record_event as record_event_task
from redash.utils import json_dumps
from sqlalchemy import cast
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import sort_query

routes = Blueprint('redash', __name__, template_folder=settings.fix_assets_path('templates'))


##########################所有api的基类
class BaseResource(Resource):
    decorators = [login_required]

    def __init__(self, *args, **kwargs):
        super(BaseResource, self).__init__(*args, **kwargs)
        self._user = None

    def dispatch_request(self, *args, **kwargs):
        kwargs.pop('org_slug', None)

        return super(BaseResource, self).dispatch_request(*args, **kwargs)

    @property
    def current_user(self):
        return current_user._get_current_object()

    @property
    def current_org(self):
        return current_org._get_current_object()

    # 请求记录器, 用于FLASK_RESTFUL API

    def record_event(self, options):
        record_event(self.current_org, self.current_user, options)

    # TODO: this should probably be somewhere else
    def update_model(self, model, updates):
        for k, v in updates.items():
            setattr(model, k, v)


##########################所有api的基类

# 请求记录器, 用于传统的url请求
#  用户自定义埋点？？？
# 记录 用户的的user_id，组织，访问的页面，动作，client相关信息

def record_event(org, user, options):
    if user.is_api_user():
        options.update({
            'api_key': user.name,
            'org_id': org.id
        })
    else:
        options.update({
            'user_id': user.id,
            'user_name': user.name,
            'org_id': org.id
        })

    options.update({
        'user_agent': request.user_agent.string,
        'ip': request.remote_addr
    })

    if 'timestamp' not in options:
        options['timestamp'] = int(time.time())

    record_event_task.delay(options)


###########################

###参数缺失，400， 返回bad request
def require_fields(req, fields):
    for f in fields:
        if f not in req:
            abort(400)


#####获得或者404 小工具

# AlertSubscription.query.get_or_404(subscriber_id)

def get_object_or_404(fn, *args, **kwargs):
    try:
        rv = fn(*args, **kwargs)
        if rv is None:
            abort(404)
    except NoResultFound:
        abort(404)
    return rv


######################


def paginate(query_set, page, page_size, serializer, **kwargs):
    count = query_set.count()

    if page < 1:
        abort(400, message='Page must be positive integer.')

        ##############################


    #我觉得这种可读性更好

    # 取最大分页数
    # import math
    # max_page = math.ceil(count / page_size)
    # if page > max_page:
    #     abort(400, message='Page is out of range.')

    ##############################
    if (page - 1) * page_size + 1 > count > 0:
        abort(400, message='Page is out of range.')

    # 每页最多250，再多前端页面屏幕不够大了？
    if page_size > 250 or page_size < 1:
        abort(400, message='Page size is out of range (1-250).')

    # data = db.session.query(MyDataClass3).paginate(2,5)
    # 5个5个的分，取第2页内的元素
    results = query_set.paginate(page, page_size)

    # support for old function based serializers

    # from inspect import isclass
    if isclass(serializer):
        items = serializer(results.items, **kwargs).serialize()
    else:
        items = [serializer(result) for result in results.items]

    return {
        'count': count,
        'page': page,
        'page_size': page_size,
        'results': items,
    }


def org_scoped_rule(rule):
    if settings.MULTI_ORG:
        return "/<org_slug:org_slug>{}".format(rule)

    return rule


########################自定义flask的json类型response的转换#############
# jsonify的源码

# return current_app.response_class( (dumps(data, indent=indent, separators=separators), '\n'),
#     mimetype=current_app.config['JSONIFY_MIMETYPE']
# )

def json_response(response):
    return current_app.response_class(json_dumps(response), mimetype='application/json')


def filter_by_tags(result_set, column):
    if request.args.getlist('tags'):
        tags = request.args.getlist('tags')
        result_set = result_set.filter(cast(column, postgresql.ARRAY(db.Text)).contains(tags))

    return result_set


def order_results(results, default_order, orders_whitelist):
    """
    Orders the given results with the sort order as requested in the
    "order" request query parameter or the given default order.
    """
    # See if a particular order has been requested
    order = request.args.get('order', '').strip() or default_order
    # and if it matches a long-form for related fields, falling
    # back to the default order
    selected_order = orders_whitelist.get(order, default_order)
    # The query may already have an ORDER BY statement attached
    # so we clear it here and apply the selected order
    return sort_query(results.order_by(None), selected_order)

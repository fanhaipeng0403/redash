from flask import jsonify

# redash __init__.py文件里
# setup_authentication(app)
# login_manager.init_app(app)
from flask_login import login_required

from redash.handlers.api import api
from redash.handlers.base import routes
from redash.monitor import get_status
from redash.permissions import require_super_admin


# Handler的总入口，放一个用于诊断的ping接口，最佳实践
# routes用的也不是内置的，而是总蓝图
@routes.route('/ping', methods=['GET'])
def ping():
    return 'PONG.'


# 系统状态。redis内存，运行了多久，日志数量，任务队列情况，文章的数目等等等(需要超级运用权限）
@routes.route('/status.json')
@login_required
@require_super_admin
def status_api():
    status = get_status()
    return jsonify(status)


# 项目http总注册接口，暴露给__init__.py的create_app使用
def init_app(app):
    # 蓝图以及一些分散的接口
    from redash.handlers import embed, queries, static, authentication, admin, setup, organization
    app.register_blueprint(routes)

    ####总API注册入口
    api.init_app(app)
    # from flask_restful import Api
    # api是API的实例

# 路由注册, 资源注册url的两种方式
#  第一种
#######################

# >> @resource.route('/local_resource)
# >> def resource():
# >>     pass


#  第二种
#######################

# >> resource.add_url_rule("/local_resource", view_func=LocalResource.as_view(name="get_local_resource"))

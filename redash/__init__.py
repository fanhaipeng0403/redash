######################软件日志#####################
import logging
import os
import sys
import urllib

################缓存数据库#######################
import redis
import urlparse
########################Web框架#################
from flask import Flask, safe_join
from flask_limiter import Limiter
########################W插件#################
from flask_limiter.util import get_ipaddr
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sslify import SSLify
########################项目配置#################
from redash import settings
######任务队列#################################
from redash.destinations import import_destinations
from redash.query_runner import import_query_runners
from statsd import StatsClient
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.routing import BaseConverter, ValidationError

#####定制服务器######

# 入口文件指定版本号,是个好习惯
__version__ = '5.0.0-beta'


# 线上现在是
# __version__ = '6.0.0-beta'
# 说明是个大版本了，不兼容


def setup_logging():
    handler = logging.StreamHandler(sys.stdout if settings.LOG_STDOUT else sys.stderr)
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(settings.LOG_LEVEL)

    # Make noisy libraries less noisy
    if settings.LOG_LEVEL != "DEBUG":
        # 所有的程序模块公用一个logging，即使依赖文件，也会写入文件'
        logging.getLogger("passlib").setLevel("ERROR")
        logging.getLogger("requests.packages.urllib3").setLevel("ERROR")
        logging.getLogger("snowflake.connector").setLevel("ERROR")
        logging.getLogger('apiclient').setLevel("ERROR")


def create_redis_connection():
    logging.debug("Creating Redis connection (%s)", settings.REDIS_URL)
    redis_url = urlparse.urlparse(settings.REDIS_URL)

    if redis_url.scheme == 'redis+socket':
        qs = urlparse.parse_qs(redis_url.query)
        if 'virtual_host' in qs:
            db = qs['virtual_host'][0]
        else:
            db = 0

        r = redis.StrictRedis(unix_socket_path=redis_url.path, db=db)
    else:
        if redis_url.path:
            redis_db = redis_url.path[1]
        else:
            redis_db = 0
        # Redis passwords might be quoted with special characters
        redis_password = redis_url.password and urllib.unquote(redis_url.password)
        r = redis.StrictRedis(host=redis_url.hostname, port=redis_url.port, db=redis_db, password=redis_password)

    return r


# 配置日志文件
# https://cuiqingcai.com/6080.html
setup_logging()

# 连接Nosql
redis_connection = create_redis_connection()
mail = Mail()
migrate = Migrate()
mail.init_mail(settings.all_settings())

############################################
## 收集各种指标
# 指标metrics指的就是各种，随时间变化可度量的值
statsd_client = StatsClient(host=settings.STATSD_HOST, port=settings.STATSD_PORT, prefix=settings.STATSD_PREFIX)
##############################################


limiter = Limiter(key_func=get_ipaddr, storage_uri=settings.LIMITER_STORAGE)

#################
# Python中所有加载到内存的模块都放在sys.modules。
# 当import一个模块时首先会在这个列表中查找是否已经加载了此模块，如果加载了则只是将模块的名字加入到正在调用import的模块的Local名字空间中。
# 如果没有加载则从sys.path目录中按照模块名称查找模块文件，模块文件可以是py、pyc、pyd，找到后将模块载入内存，并加入到sys.modules中，并将名称导入到当前的Local名字空间。

# 利用import首次导入时候的初始化,执行了
# register(BigQuery)
# register(BigQueryGCE)

# 我觉得还是导入进来这个函数，
# 然后手动register()更好????


# 学习这种插件式的配置方法
import_query_runners(settings.QUERY_RUNNERS)
# 'redash.query_runner.memsql_ds',
# 'redash.query_runner.athena',
# 'redash.query_runner.big_query',


import_destinations(settings.DESTINATIONS)
#################

# https://www.zhihu.com/question/19887316
#######
# redash包从version_check导入reset_new_version_status,  from redash.version_check import reset_new_version_status
# version_check模块从redash包导入current_version, from redash import __version__ as current_version
# 产生了循环导入,相互依赖

# import本质也是执行指令，如果导入reset_new_version_status放到__version__ = '5.0.0-beta'前面，
# 执行 from redash.version_check import reset_new_version_status的时候
# version_check(首次进入sys.module)初始化时，执行到 from redash import __version__ as current_version,会导入不仅current_version，因为还没定义
from redash.version_check import reset_new_version_status

reset_new_version_status()


class SlugConverter(BaseConverter):
    def to_python(self, value):
        # This is ay workaround for when we enable multi-org and some files are being called by the index rule:
        for path in settings.STATIC_ASSETS_PATHS:
            full_path = safe_join(path, value)
            if os.path.isfile(full_path):
                raise ValidationError()

        return value

    def to_url(self, value):
        return value



###create_app用在了4个地方
# 1.wsgi
# 2.runserver 开发
# 3.celery的worker上下文集成
# 4.测试test
def create_app(load_admin=True):

    # 1.redash的__init___文件包含了一些通用的函数或者变量
    # 2.下面引入的模块使用了从这个模块导出的变量
    # 3.这里又从这些模块，导入进来一些函数或者变量
    # 4.形成了相互依赖
    # 5.解决方案
    # 6.调用置后于初始化的过程，比如requeset文件中的使用的 from redash import statsd_client 一定要在 from redash.metrics.request import provision_app前面
    # 7.或者放入函数内部
    # 8.保证首次进入sys.moudle的模块，已经包含了那些初始化的通用变量

    # import语句中的 模块 包含了这个import语句所在模块的 依赖，那么这个import语句应该在这个依赖声明的后面

    from redash import extensions, handlers
    from redash.handlers.webpack import configure_webpack
    from redash.handlers import chrome_logger
    from redash.admin import init_admin
    from redash.models import db
    from redash.authentication import setup_authentication
    from redash.metrics.request import provision_app

    # https: // www.v2ex.com / t / 289972

    # 创建 flask 对象时候，是需要传一个模块一般是__name__过去，你改下就行了，那个是被当作根地址,确定了template位置
    # 也可以在蓝图的时候指定

    app = Flask(__name__,
                # 指定静态文件目录
                # fix_assets_path(os.environ.get("REDASH_STATIC_ASSETS_PATH", "../client/dist/"))
                template_folder=settings.STATIC_ASSETS_PATH,

                # https://blog.csdn.net/qq_40952927/article/details/81157204
                static_folder=settings.STATIC_ASSETS_PATH,
                static_path='/static')

    # https://www.kancloud.cn/wizardforcel/explore-flask/140842
    # http://python.jobbole.com/84003/
    # 使用了Nginx后，为了获取真实的请求IP
    app.wsgi_app = ProxyFix(app.wsgi_app, settings.PROXIES_COUNT)

    #  定制url
    app.url_map.converters['org_slug'] = SlugConverter

    # 根据setting文件配置
    if settings.ENFORCE_HTTPS:
        # https: // www.helplib.com / GitHub / article_82448
        # 所有的http重定向为https
        # 什么时候使用 ??????????????????????
        SSLify(app, skips=['ping'])

    # 异常警报和通知处理

    if settings.SENTRY_DSN:
        from raven import Client
        from raven.contrib.flask import Sentry
        from raven.handlers.logging import SentryHandler

        client = Client(settings.SENTRY_DSN, release=__version__, install_logging_hook=False)
        sentry = Sentry(app, client=client)
        sentry.client.release = __version__

        sentry_handler = SentryHandler(client=client)
        sentry_handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(sentry_handler)

    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI

    # 默认自带的配置
    app.config.update(settings.all_settings())

    # 插件和自定义插件初始化
    if load_admin:
        init_admin(app)

    # 数据库
    # db = SQLAlchemy(app)
    db.init_app(app)


    # 数据库迁移
    migrate.init_app(app, db)
    # 邮件
    mail.init_app(app)
    # 请求次数
    limiter.init_app(app)
    # logger
    chrome_logger.init_app(app)
    extensions.init_extensions(app)

    # 一些请求前后的狗子，用于性能测试等
    provision_app(app)

    # 所有的controller入口！！！！！

    handlers.init_app(app)

    # api 认证接口注册！！！！
    setup_authentication(app)

    # webpack!!!!!
    configure_webpack(app)

    return app

# 入口文件创立flask app
# 初始化一些任务

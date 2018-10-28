import logging
import sys
import urllib

import redis
import urlparse
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sslify import SSLify
from redash import settings
from redash.destinations import import_destinations
from redash.query_runner import import_query_runners
from statsd import StatsClient
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.routing import BaseConverter

# 入口文件指定版本号,是个好习惯
__version__ = '5.0.0-beta'


def setup_logging():
    handler = logging.StreamHandler(sys.stdout if settings.LOG_STDOUT else sys.stderr)
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(settings.LOG_LEVEL)

    # Make noisy libraries less noisy
    if settings.LOG_LEVEL != "DEBUG":
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
setup_logging()


# 连接Nosql
redis_connection = create_redis_connection()
mail = Mail()
migrate = Migrate()
mail.init_mail(settings.all_settings())
statsd_client = StatsClient(host=settings.STATSD_HOST, port=settings.STATSD_PORT, prefix=settings.STATSD_PREFIX)
limiter = Limiter(key_func=get_ipaddr, storage_uri=settings.LIMITER_STORAGE)

import_query_runners(settings.QUERY_RUNNERS)
import_destinations(settings.DESTINATIONS)

from redash.version_check import reset_new_version_status

reset_new_version_status()


class SlugConverter(BaseConverter):
    def to_python(self, value):
        # This is ay workaround for when we enable multi-org and some files are being called by the index rule:
        # for path in settings.STATIC_ASSETS_PATHS:
        #     full_path = safe_join(path, value)
        #     if os.path.isfile(full_path):
        #         raise ValidationError()

        return value

    def to_url(self, value):
        return value


def create_app(load_admin=True):
    from redash import extensions, handlers
    from redash.handlers.webpack import configure_webpack
    from redash.handlers import chrome_logger
    from redash.admin import init_admin
    from redash.models import db
    from redash.authentication import setup_authentication
    from redash.metrics.request import provision_app

    app = Flask(__name__,
                # 指定静态文件目录
                # fix_assets_path(os.environ.get("REDASH_STATIC_ASSETS_PATH", "../client/dist/"))
                template_folder=settings.STATIC_ASSETS_PATH,
                static_folder=settings.STATIC_ASSETS_PATH,
                static_path='/static')

    # Make sure we get the right referral address even behind proxies like nginx.
    # 难点。。。。
    app.wsgi_app = ProxyFix(app.wsgi_app, settings.PROXIES_COUNT)


    # https: // allenwind.github.io / 2017 / 12 / 29 / Flask % E8 % 87 % AA % E5 % AE % 9 A % E4 % B9 % 89 URL - Converter /
    #  定制url
    app.url_map.converters['org_slug'] = SlugConverter

    # 根据setting文件配置
    if settings.ENFORCE_HTTPS:
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

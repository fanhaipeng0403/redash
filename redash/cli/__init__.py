from __future__ import print_function

import json

import click
from flask import current_app
from flask.cli import FlaskGroup, run_command
from redash import create_app, settings, __version__
from redash.cli import users, groups, database, data_sources, organization
from redash.monitor import get_status


#######################这样可以#######################
def foo():
    """132132132"""


def create(group):
    app = current_app or create_app()
    group.app = app

    @app.shell_context_processor
    def shell_context():
        ##shell 通常 包含数据库的Model模型
        from redash import models
        return dict(models=models)

    return app


# https://isudox.com/2016/09/03/learning-python-package-click/


# 实际执行的是这个
# FlaskGroup(manager,create_app)

# @click.group 装饰器把方法装饰为
# 可以拥有多个子命令的 Group 对象
# 由 Group.add_command() 方法把 Command 对象关联到 Group 对象。
@click.group(cls=FlaskGroup, create_app=create)
def manager():
    """Management script for Redash"""


################数据库操作###############
manager.add_command(database.manager, "database")

##############################
manager.add_command(users.manager, "users")
manager.add_command(groups.manager, "groups")
manager.add_command(data_sources.manager, "ds")
manager.add_command(organization.manager, "org")
manager.add_command(users.manager, "users")
##############################


###内置的runserver命令
manager.add_command(run_command, "runserver")


# 也可以直接用 @Group.command 装饰方法，会自动把方法关联到该 Group 对象下。
@manager.command()
def version():
    """Displays Redash version."""
    print(__version__)



################应用状态################
@manager.command()
def status():
    print(json.dumps(get_status(), indent=2))



################配置检查################
@manager.command()
def check_settings():
    """Show the settings as Redash sees them (useful for debugging)."""
    for name, item in settings.all_settings().iteritems():
        print("{} = {}".format(name, item))


################测试邮件服务器################
@manager.command()
@click.argument('email', default=settings.MAIL_DEFAULT_SENDER, required=False)
def send_test_mail(email=None):
    """
    Send test message to EMAIL (default: the address you defined in MAIL_DEFAULT_SENDER)
    """
    from redash import mail
    from flask_mail import Message

    if email is None:
        email = settings.MAIL_DEFAULT_SENDER

    mail.send(Message(subject="Test Message from Redash", recipients=[email],
                      body="Test message."))


@manager.command()
def ipython():
    """Starts IPython shell instead of the default Python shell."""
    import sys
    import IPython
    from flask.globals import _app_ctx_stack
    app = _app_ctx_stack.top.app

    banner = 'Python %s on %s\nIPython: %s\nRedash version: %s\n' % (
        sys.version,
        sys.platform,
        IPython.__version__,
        __version__
    )

    ctx = {}
    ctx.update(app.make_shell_context())

    IPython.embed(banner1=banner, user_ns=ctx)

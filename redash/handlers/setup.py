from flask import g, redirect, render_template, request, url_for

from flask_login import login_user
from redash import settings
from redash.authentication.org_resolving import current_org
from redash.handlers.base import routes
from redash.models import Group, Organization, User, db
from redash.tasks.general import subscribe
from wtforms import BooleanField, Form, PasswordField, StringField, validators
from wtforms.fields.html5 import EmailField


#########定制Form
class SetupForm(Form):
    name = StringField('Name', validators=[validators.InputRequired()])
    email = EmailField('Email Address', validators=[validators.Email()])
    password = PasswordField('Password', validators=[validators.Length(6)])
    org_name = StringField("Organization Name", validators=[validators.InputRequired()])
    security_notifications = BooleanField()
    # 给读者定期发送邮件等,是否接受
    newsletter = BooleanField()


def create_org(org_name, user_name, email, password):
    ###############################创建组织和分组
    # default_org = Organization.create(name=org_name, slug='default', settings={})
    # admin_group = Group.create(name='admin', permissions=['admin', 'super_admin'], org=default_org, type=Group.BUILTIN_GROUP)
    # default_group = Group.create(name='default', permissions=Group.DEFAULT_PERMISSIONS, org=default_org, type=Group.BUILTIN_GROUP)

    default_org = Organization(name=org_name, slug='default', settings={})

    admin_group = Group(name='admin', permissions=['admin', 'super_admin'], org=default_org, type=Group.BUILTIN_GROUP)

    default_group = Group(name='default', permissions=Group.DEFAULT_PERMISSIONS, org=default_org,
                          type=Group.BUILTIN_GROUP)

    db.session.add_all([default_org, admin_group, default_group])
    db.session.commit()

    ###############################创建用户
    user = User(org=default_org, name=user_name, email=email, group_ids=[admin_group.id, default_group.id])
    ####  不保存密码，直接hash进去
    user.hash_password(password)
    ####
    db.session.add(user)
    db.session.commit()

    return default_org, user


@routes.route('/setup', methods=['GET', 'POST'])
def setup():
    ##############################################################################################
    ## 已经配置过，重定向到首页
    if current_org != None or settings.MULTI_ORG:
        return redirect('/')

    ##############################################################################################

    form = SetupForm(request.form)

    # 相关form默认设置为True
    form.newsletter.data = True
    form.security_notifications.data = True

    ####创建成功
    if request.method == 'POST' and form.validate():

        default_org, user = create_org(form.org_name.data, form.name.data, form.email.data, form.password.data)

        g.org = default_org

        # current_user, login_required, login_user, logout_user
        # login_manager = LoginManager()
        # login_manager.init_app(app)

        login_user(user)

        if form.newsletter.data or form.security_notifications:
            subscribe.delay(form.data)

        # D:\redash - master\redash\handlers\static.py
        return redirect(url_for('redash.index', org_slug=None))

    return render_template('setup.html', form=form)

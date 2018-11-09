""""
# API开始设计?????????????????????????????????????????????????????????????????????
RESTFUL API URL 设计


http://www.ruanyifeng.com/blog/2014/05/restful_api.html


1.版本

/v1

2.语义化路径

/v1/users

3.分层过滤

/v1/users/2

4.HTTP动词

GET /v1/users/2

5.适当冗余

GET /v1/users?user_id=2

6.返回状态码,错误信息

{status: 200, error:‘xxxx’ }

7.返回结果

GET /collection：返回资源对象的列表（数组）
GET /collection/resource：返回单个资源对象
POST /collection：返回新生成的资源对象
PUT /collection/resource：返回完整的资源对象
PATCH /collection/resource：返回完整的资源对象
DELETE /collection/resource：返回一个空文档

8.身份认证, 使用OAuth 2.0框架。



#######################################################################

通常有这样的两个后端视图
/api/alerts
/api/alerts/<alert_id>

/api/alerts/<alert_id>/subscriptions
/api/alerts/<alert_id>/subscriptions/<subscriber_id>


"""
import time

from flask import request
from funcy import project
from redash import models
from redash.handlers.base import (BaseResource, get_object_or_404,
                                  require_fields)
from redash.permissions import (require_access, require_admin_or_owner,
                                require_permission, view_only)
from redash.serializers import serialize_alert


# 注册到 api.add_org_resource(AlertResource, '/api/alerts/<alert_id>', endpoint='alert')
# 导出api到handler的__init__.py
# api.init_app(app)

class AlertResource(BaseResource):
    def get(self, alert_id):
        alert = get_object_or_404(models.Alert.get_by_id_and_org, alert_id, self.current_org)
        require_access(alert.groups, self.current_user, view_only)
        return serialize_alert(alert)

    def post(self, alert_id):
        req = request.get_json(True)
        params = project(req, ('options', 'name', 'query_id', 'rearm'))
        alert = get_object_or_404(models.Alert.get_by_id_and_org, alert_id, self.current_org)
        require_admin_or_owner(alert.user.id)

        self.update_model(alert, params)
        models.db.session.commit()

        self.record_event({
            'action': 'edit',
            'timestamp': int(time.time()),
            'object_id': alert.id,
            'object_type': 'alert'
        })

        return serialize_alert(alert)

    def delete(self, alert_id):
        alert = get_object_or_404(models.Alert.get_by_id_and_org, alert_id, self.current_org)
        require_admin_or_owner(alert.user_id)
        models.db.session.delete(alert)
        models.db.session.commit()


# api.add_org_resource(AlertListResource,'/api/alerts', endpoint='alerts')
class AlertListResource(BaseResource):
    def post(self):
        req = request.get_json(True)
        require_fields(req, ('options', 'name', 'query_id'))

        query = models.Query.get_by_id_and_org(req['query_id'],
                                               self.current_org)
        require_access(query.groups, self.current_user, view_only)

        alert = models.Alert(
            name=req['name'],
            query_rel=query,
            user=self.current_user,
            rearm=req.get('rearm'),
            options=req['options']
        )

        models.db.session.add(alert)
        models.db.session.flush()
        models.db.session.commit()

        self.record_event({
            'action': 'create',
            'timestamp': int(time.time()),
            'object_id': alert.id,
            'object_type': 'alert'
        })

        return serialize_alert(alert)

    @require_permission('list_alerts')
    def get(self):
        return [serialize_alert(alert) for alert in models.Alert.all(group_ids=self.current_user.group_ids)]


# api.add_org_resource(AlertSubscriptionListResource, '/api/alerts/<alert_id>/subscriptions', endpoint='alert_subscriptions')
class AlertSubscriptionListResource(BaseResource):
    def post(self, alert_id):
        req = request.get_json(True)

        alert = models.Alert.get_by_id_and_org(alert_id, self.current_org)
        require_access(alert.groups, self.current_user, view_only)
        kwargs = {'alert': alert, 'user': self.current_user}

        if 'destination_id' in req:
            destination = models.NotificationDestination.get_by_id_and_org(req['destination_id'], self.current_org)
            kwargs['destination'] = destination

        subscription = models.AlertSubscription(**kwargs)
        models.db.session.add(subscription)
        models.db.session.commit()

        self.record_event({
            'action': 'subscribe',
            'timestamp': int(time.time()),
            'object_id': alert_id,
            'object_type': 'alert',
            'destination': req.get('destination_id')
        })

        d = subscription.to_dict()
        return d

    def get(self, alert_id):
        alert_id = int(alert_id)
        alert = models.Alert.get_by_id_and_org(alert_id, self.current_org)
        require_access(alert.groups, self.current_user, view_only)

        subscriptions = models.AlertSubscription.all(alert_id)
        return [s.to_dict() for s in subscriptions]


# api.add_org_resource(AlertSubscriptionResource, '/api/alerts/<alert_id>/subscriptions/<subscriber_id>', endpoint='alert_subscription')
class AlertSubscriptionResource(BaseResource):
    def delete(self, alert_id, subscriber_id):
        subscription = models.AlertSubscription.query.get_or_404(subscriber_id)
        require_admin_or_owner(subscription.user.id)
        models.db.session.delete(subscription)
        models.db.session.commit()

        self.record_event({
            'action': 'unsubscribe',
            'timestamp': int(time.time()),
            'object_id': alert_id,
            'object_type': 'alert'
        })

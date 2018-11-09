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
/api/alerts             xxxxxxListResouce

/api/alerts/<alert_id>   xxxxxxResouce

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

session = models.db.session

# 注册到 api.add_org_resource(AlertResource, '/api/alerts/<alert_id>', endpoint='alert')
# 导出api到handler的__init__.py
# api.init_app(app)



# 更新某个alert

class AlertResource(BaseResource):
    def get(self, alert_id):
        
        alert = get_object_or_404(models.Alert.get_by_id_and_org, alert_id, self.current_org)
        
        require_access(alert.groups, self.current_user, view_only)
        
         # serialize_alert 对返回的查询列，进行特定处理，转换为前端需要的json
        
        return serialize_alert(alert)

    def post(self, alert_id):

        ## 获得参数
        req = request.get_json(True)

        ## 提取参数
        params = project(req, ('options', 'name', 'query_id', 'rearm'))

        ## 根据参数查询
        alert = get_object_or_404(models.Alert.get_by_id_and_org, alert_id, self.current_org)

        ##判断权限
        require_admin_or_owner(alert.user.id)


        ######
        # for k, v in updates.items():
        #     setattr(model, k, v)


        #进行更新
        self.update_model(alert, params)
        #######


        #提交更新
        session.commit()

        self.record_event({
            'action': 'edit',
            'timestamp': int(time.time()),
            'object_id': alert.id,
            'object_type': 'alert'
        })

        # serialize_alert 对返回的查询列，进行特定处理，转换为前端需要的json

        return serialize_alert(alert)

    def delete(self, alert_id):
        alert = get_object_or_404(models.Alert.get_by_id_and_org, alert_id, self.current_org)
        require_admin_or_owner(alert.user_id)
        session.delete(alert)
        session.commit()



# 创建alert,获取所有alerts

# /api/alerts',这里注意POST，是针对创建一个alerts，只是放到这里了
# api.add_org_resource(AlertListResource,'/api/alerts', endpoint='alerts')
class AlertListResource(BaseResource):
    def post(self):

        #忽视mimetype类型，强制为Json类型

        req = request.get_json(True)

        # 判断请求参数
        require_fields(req, ('options', 'name', 'query_id'))

        #### 根据哪个query_id创建的alert
        query = models.Query.get_by_id_and_org(req['query_id'], self.current_org)

        ## 权限系统？？？？？？？？？？？？？？
        require_access(query.groups, self.current_user, view_only)

        # query_rel 是 relationShip， 传对方的行对象,需要提供
        # 但是不用提供外键对应的列
        alert = models.Alert( name=req['name'], query_rel=query,
                              user=self.current_user, rearm=req.get('rearm'), options=req['options'] )

        session.add(alert)
        session.flush()
        session.commit()

        self.record_event({
            'action': 'create',
            'timestamp': int(time.time()),
            'object_id': alert.id,
            'object_type': 'alert'
        })


        ### RESETFUL 规范， 不能只是响应个200，就完事了， 最好把创建好的东西返回给前端
        return serialize_alert(alert)

    @require_permission('list_alerts')
    def get(self):
        return [serialize_alert(alert) for alert in models.Alert.all(group_ids=self.current_user.group_ids)]



# api.add_org_resource(AlertSubscriptionListResource, '/api/alerts/<alert_id>/subscriptions', endpoint='alert_subscriptions')


    # alerts, s 通常有个all的类方法
    # @classmethod
    # def all(c

class AlertSubscriptionListResource(BaseResource):
    def post(self, alert_id):
        req = request.get_json(True)

        alert = models.Alert.get_by_id_and_org(alert_id, self.current_org)
        require_access(alert.groups, self.current_user, view_only)



        kwargs = {'alert': alert, 'user': self.current_user}

        if 'destination_id' in req:
            destination = models.NotificationDestination.get_by_id_and_org(req['destination_id'], self.current_org)
            kwargs['destination'] = destination

        # 用提供外键对应的列
        # kwargs = {'alert': alert, 'user': self.current_user, 'destination': destination}

        # AlertSubscription. 一个alert有对应多个订阅者，一订阅者订阅多个alert，多对多

        # alert
        # user
        # query
        # notification

        subscription = models.AlertSubscription(**kwargs)
        session.add(subscription)
        session.commit()

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



# 退订，那个用户退订了那个alert
# api.add_org_resource(AlertSubscriptionResource, '/api/alerts/<alert_id>/subscriptions/<subscriber_id>', endpoint='alert_subscription')
class AlertSubscriptionResource(BaseResource):
    def delete(self, alert_id, subscriber_id):
        subscription = models.AlertSubscription.query.get_or_404(subscriber_id)
        require_admin_or_owner(subscription.user.id)
        session.delete(subscription)
        session.commit()

        self.record_event({
            'action': 'unsubscribe',
            'timestamp': int(time.time()),
            'object_id': alert_id,
            'object_type': 'alert'
        })

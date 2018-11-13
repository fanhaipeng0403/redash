
########################################################################################

 首次登陆的时候的 闪现信息

 login_manager.login_message = "来了，老弟”

########################################################################################

 ResultFul 使用login_required

 from flask_restful import Resource, abort
 from flask_login import current_user, login_required

 class BaseResource(Resource):
     decorators = [login_required]

########################################################################################

 https://flask-login.readthedocs.io/en/latest/ 对匿名定制权限
 login_manager.anonymous_user = AnonymousUser

########################################################################################

 指定未注册用户的处理办法

 login.login_view = "account.sign_in"

 或者使用 @login_manager.unauthorized_handler
 @login_manager.unauthorized_handler
 def redirect_to_login():
     if request.is_xhr or '/api/' in request.path:
         response = jsonify({'message': "Couldn't find resource. Please login and try again."})
         response.status_code = 404
         return response

     login_url = get_login_url(next=request.url, external=False)

     return redirect(login_url)

########################################################################################

 如果你不想使用cookie ，而是用request的header值或者api key，请使用 @login_manager.request_loader, 通常用于Http Basic Auth等，第三方认证

 D:\redash-master\redash\authentication\__init__.py

 def load_user_from_request(request):
         pass
 login_manager.request_loader(hmac_load_user_from_request)

##############################################################
 最佳实践，添加/api/session

`
 @routes.route(org_scoped_rule('/api/session'), methods=['GET'])
@login_required
 def session(org_slug=None):
     if current_user.is_api_user():
         user = {
             'permissions': [],
             'apiKey': current_user.id
         }
     else:
         user = {
             'profile_image_url': current_user.profile_image_url,
             'id': current_user.id,
             'name': current_user.name,
             'email': current_user.email,
             'groups': current_user.group_ids,
             'permissions': current_user.permissions
         }
     return json_response({
         'user': user,
         'org_slug': current_org.slug,
         'client_config': client_config()
     })
`

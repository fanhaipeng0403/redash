HTTP基本认证（HTTP Basic Auth）

在HTTP中，HTTP基本认证是一种允许Web浏览器或者其他客户端在请求时提供用户名和口令形式的身份凭证的一种登录验证方式。
简单而言，HTTP基本认证就是我们平时在网站中最常用的通过用户名和密码登录来认证的机制。 


# 优点 
HTTP 基本认证是基本上所有流行的网页浏览器都支持。但是基本认证很少在可公开访问的互联网网站上使用，有时候会在小的私有系统中使用。 
# 缺点 
HTTP 基本认证虽然足够简单，但是前提是在客户端和服务器主机之间的连接足够安全。如果没有使用SSL/TLS这样的传输层安全的协议，那么以明文传输的密钥和口令很容易被拦截。 
由于现存的浏览器保存认证信息直到标签页或浏览器关闭，或者用户清除历史记录。导致了服务器端无法主动来当前用户登出或者认证失效

--------------------- 
原文：https://blog.csdn.net/qq673318522/article/details/62047574 


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

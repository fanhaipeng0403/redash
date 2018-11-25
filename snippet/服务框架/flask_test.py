from functools import wraps

from flask import Flask, render_template, send_file, jsonify, redirect
from flask import g

###指定template目录
app = Flask(__name__, template_folder='./')


# 中间件
# http://docs.jinkan.org/docs/flask/patterns/appdispatch.html#app-dispatch
class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        print(environ)
        print(start_response)
        return self.app(environ, start_response)


app.wsgi_app = ReverseProxied(app.wsgi_app)


#
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#
#         print(dir(g))
#         if not getattr(g, 'user', None):
#             return '未登录'
#         return f(*args, **kwargs)
#
#     return decorated_function


#####多个路由
@app.route('/xxx')
@login_required
def foo():
    response = render_template("test.py")
    return response


@app.route('/zzz')
def foo1():
    ###直接渲染文件内容,或作为附件
    response = send_file("test.py")
    return response


@app.route('/yyy')
def foo2():
    # 几种方式
    # return jsonify(a=1)
    # return jsonify({'a':1})
    # return jsonify({'a':1},{'b':2})
    return jsonify(a=1, b=2)


if __name__ == '__main__':
    app.run(debug=True)

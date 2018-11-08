from flask import render_template, safe_join, send_file

from flask_login import login_required
from redash import settings
from redash.handlers.authentication import base_href
from redash.handlers.base import org_scoped_rule, routes


###  app.send_static_file
###  app.send_static_file 发送静态文件

# >>>>@app.route("/download/<filepath>", methods=['GET'])
# >>>> def download_file(filepath):
#     此处的filepath是文件的路径，但是文件必须存储在static文件夹下， 比如images\test.jpg
#  >>>>>return app.send_static_file(filepath)

def render_index():
    if settings.MULTI_ORG:
        # base_href ,项目的完整根路径
        # base_href = url_for('redash.index', _external=True), _external显示完整路径

        # app = Flask(__name__, template_folder='./'), 在app创建的,指定项目template的目录,也就是multi_org.html的位置
        response = render_template("multi_org.html", base_href=base_href())

        # base标签

        # 我们设置base标签，给一个基准href，那么其他的链接都是以此为基准

        # < base href = "{{base_href}}" >

    else:
        #  path =  directory + filename
        #  文件路径 =  目录 + 文件名
        # safe_join , 目录和文件名，合成文件的绝对路径
        full_path = safe_join(settings.STATIC_ASSETS_PATH, 'index.html')

        response = send_file(full_path, **dict(cache_timeout=0, conditional=True))

        # response = send_file(full_path, **dict(cache_timeout=0, conditional=True)), 直接渲染文件的内容到页面里.
        #（为什么不用reader_template)，(可能不受template设置的项目路径的影响）

        # response = send_file(full_path, as_attachment=True) 添加as_attachment=True的话， 将作为附件下载

    return response


@routes.route(org_scoped_rule('/<path:path>'))
# /<path:path>
# /<org_slug:org_slug>/<path:path>
@routes.route(org_scoped_rule('/'))
# /
# /<org_slug:org_slug>
@login_required
def index(**kwargs):
    return render_index()

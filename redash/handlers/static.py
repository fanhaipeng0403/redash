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
        response = render_template("multi_org.html", base_href=base_href())
    else:

        #  path =  directory + filename
        #  文件路径 =  目录 + 文件名
        # safe_join , 目录和文件名，合成文件的绝对路径
        full_path = safe_join(settings.STATIC_ASSETS_PATH, 'index.html')
        response = send_file(full_path, **dict(cache_timeout=0, conditional=True))

    return response


@routes.route(org_scoped_rule('/<path:path>'))
@routes.route(org_scoped_rule('/'))
@login_required
def index(**kwargs):
    return render_index()

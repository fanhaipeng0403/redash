import logging

from flask import g, request
from redash.models import Organization
from werkzeug.local import LocalProxy


def _get_current_org():
    if 'org' in g:
        return g.org

    slug = request.view_args.get('org_slug', g.get('org_slug', 'default'))

    # slug 翻译过来就是：标称， 单位的意思。在 django 中，slug 指有效 URL 的一部分，能使 URL 更加清晰易懂。比如有这样一篇文章，标题是 "13岁的孩子"，
    # 它的 URL 地址是 "/posts/13-sui-de-hai-zi"，后面这一部分便是 slug。

    g.org = Organization.get_by_slug(slug)
    logging.debug("Current organization: %s (slug: %s)", g.org, slug)
    return g.org


# TODO: move to authentication
# local proxy[ ˈprɔksi:]

current_org = LocalProxy(_get_current_org)

# 将current_org弄成线程里的全局变量，并可以通过 current_org._get_current_object() 调用

# current_user,flask-login 的源码类似
# current_user = LocalProxy(lambda: _get_user())

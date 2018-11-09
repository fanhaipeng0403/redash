import logging

from flask import g, request
from werkzeug.local import LocalProxy

from redash.models import Organization


def _get_current_org():
    if 'org' in g:
        return g.org

    slug = request.view_args.get('org_slug', g.get('org_slug', 'default'))
    g.org = Organization.get_by_slug(slug)
    logging.debug("Current organization: %s (slug: %s)", g.org, slug)
    return g.org

# TODO: move to authentication
# local proxy[ ˈprɔksi:]

current_org = LocalProxy(_get_current_org)


# 将current_org弄成线程里的全局变量，并可以通过 current_org._get_current_object() 调用
# current_user,flask-login 的源码可借鉴

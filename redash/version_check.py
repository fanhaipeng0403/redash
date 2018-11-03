import logging
import requests
import semver

from redash import __version__ as current_version
from redash import redis_connection
#### redash已经进入了sys.module (manage.py文件),加不再初始化.初始化只进行一次
from redash.utils import json_dumps

REDIS_KEY = "new_version_available"


####celery定时查询发布版本和当前版本对比，看是否有新的了#################
def run_version_check():

    ####没指定logger就是root的？
    logging.info("Performing version check.")
    logging.info("Current version: %s", current_version)

    data = json_dumps({
        'current_version': current_version
    })
    # 用于定义网络文件的类型和网页的编码，决定浏览器将以什么形式、什么编码读取这个文件
    headers = {'content-type': 'application/json'}

    try:
        response = requests.post('https://version.redash.io/api/report?channel=stable',
                                 data=data, headers=headers, timeout=3.0)
        latest_version = response.json()['release']['version']

        _compare_and_update(latest_version)
    except requests.RequestException:
        logging.exception("Failed checking for new version.")
    except (ValueError, KeyError):
        logging.exception("Failed checking for new version (probably bad/non-JSON response).")



####启后第一次查询#################
def reset_new_version_status():
    latest_version = get_latest_version()
    if latest_version:
        _compare_and_update(latest_version)


def get_latest_version():
    return redis_connection.get(REDIS_KEY)



def _compare_and_update(latest_version):
    # http://taobaofed.org/blog/2016/08/05/instructions-of-semver/
    # Semantic Versioning, 语义化版本
    # semver

    #常规版本号
    # 0.1.0
    # 大版本（不兼容），小版本（向后兼容），修订（一些小更新）

    # 预发版本号
    # "1.0.0-beta.1"< stage > 一般选用：alpha、beta、rc。

    # 因此在版本的大小比较上，仍然先比较常规版本号部分；对于预发标记部分的比较，则是根据 ASCII 字母表中的顺序来进行。

    is_newer = semver.compare(current_version, latest_version) == -1
    logging.info("Latest version: %s (newer: %s)", latest_version, is_newer)

    if is_newer:
        redis_connection.set(REDIS_KEY, latest_version)
    else:
        redis_connection.delete(REDIS_KEY)

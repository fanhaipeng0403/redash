#!/usr/bin/env python
"""
CLI to manage redash.
"""

from redash.cli import manager

if __name__ == '__main__':
    manager()

# docker-compose文件中有
# command: dev_server,
# 就是去执行entryPoint下的 dev_server函数
# exec /app/manage.py runserver --debugger --reload -h 0.0.0.0

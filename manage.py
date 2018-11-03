#!/usr/bin/env python
"""
CLI to manage redash.
"""


# Python ___init___文件的作用

# 1. __init__.py主要控制包的导入行为


# __all__ = ["Module1", "Module2", "subPackage1", "subPackage2"]
# 当使用from package import *时，就会默认导入"Module1", "Module2", "subPackage1", "subPackage2"模块。
# import package, package.Module1


# 2. 初始化包的行为


# graphics/
#     __init__.py
#     primitive/
#         __init__.py ( print('xxxx'))
#         line.py
#         fill.py
#         text.py
#     formats/

#         __init__.py  ( print('yyyy'))
#         png.py
#         jpg.py
# 一旦你做到了这一点,执行各种import语句，如下：

# import graphics.primitive.line
# from graphics.primitive import line
# from graphics.primitive.line import a
# import graphics.formats.jpg as jpg


# 只要涉及到了包内的模块或者变量
# 会打印出xxxx和yyyy
# 即完成了初始化操作
#  因此当执行 from redash.cli import manager的时候
# redash 的__init__和cli的___init__的代码都会执行



# import导入机制

# import 'xxxxx'
# 'xxxx' 模块里的代码将执行
# 'xxxx' 模块进入 sys.module
# 再次import 'xxxxx'
# 'xxxx' 模块里的代码将不再执行

# https://zhuanlan.zhihu.com/p/29883945



from redash.cli import manager

if __name__ == '__main__':
    ### 创建app,绑定CLI管理命令
    manager()

# docker-compose文件中的 command: dev_server,
# 就是去执行entryPoint下的 dev_server函数
# exec /app/manage.py runserver --debugger --reload -h 0.0.0.0

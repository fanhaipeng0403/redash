from snippet.异常.API返回 import errors
from snippet.异常.API返回.exceptions import ApiException


def foo():
    # 提供了代码可读性,维护性
    raise ApiException(errors.not_found)

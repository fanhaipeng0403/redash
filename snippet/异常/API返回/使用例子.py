from snippet.异常.API返回 import errors
from snippet.异常.API返回.exceptions import ApiException


def foo():
    # 提供了代码可读性,维护性
    raise ApiException(errors.not_found)



# 或者直接使用abort
# def foo():
#     try:
#         1 / 0
#     except Exception as e:
#         if max_age > 0:
#             abort(404, message="1不能除以0")
#             else:
#             abort(503, message="Unable to get result from the database.")

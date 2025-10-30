# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
主要功能是一个装饰器,用于在调用某个API方法之前检查指定的对象是否存在。
如果对象不存在,它会捕获NotFound异常,并通过api_utils.not_found函数返回一个标准的404错误响应。
如果对象存在,则继续执行原本的API方法。这样可以确保API调用时对象的有效性,避免因对象不存在而导致的错误操作。
"""
import functools

from blazar.api.v1 import utils as api_utils
from blazar import exceptions


def check_exists(get_function, object_id=None, **get_args):
    """Check object exists.

    :param get_function: Method to call to get object.
    :type get_function: function
    :param object_id: ID of the object to get.
    :type object_id: str
    :param get_args: Other params to pass to the get_function method.
    :type get_args: dict
    """
    def decorator(func):
        """Decorate method to check object existing."""
        if object_id is not None:
            get_args['id'] = object_id

        @functools.wraps(func)
        def handler(*args, **kwargs):
            """Decorator handler."""

            get_kwargs = {}
            for k, v in get_args.items():
                get_kwargs[k] = kwargs[v]

            try:
                obj = get_function(**get_kwargs)
            except exceptions.NotFound:
                obj = None
            if obj is None:
                e = exceptions.NotFound(object=get_kwargs)
                return api_utils.not_found(e)

            return func(*args, **kwargs)

        return handler

    return decorator

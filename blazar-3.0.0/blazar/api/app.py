# Copyright (c) 2017 NTT Inc.
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
主要功能是根据请求的路径信息选择合适的API版本,并处理版本信息的响应。
当用户请求/或/versions时,它会返回可用的API版本信息;
当用户请求特定版本的API(如/v1或/v2)时,它会将请求路由到相应的API版本处理。
"""

from oslo_serialization import jsonutils
import six
# 导入Blazar API的v1和v2版本的应用程序模块
from blazar.api.v1 import app as v1_app
from blazar.api.v2 import app as v2_app


# 该类的主要功能是根据请求的路径信息选择合适的API版本,并处理版本信息的响应
class VersionSelectorApplication(object):
    """Maps WSGI versioned apps and defines default WSGI app."""

    def __init__(self):
        # 初始化状态码_status和响应头_response_headers为空,同时创建v1和v2版本的API应用程序实例。
        self._status = ''
        self._response_headers = []
        self.v1 = v1_app.make_app()
        self.v2 = v2_app.make_app()

    def _append_versions_from_app(self, versions, app, environ):
        """
         该方法接收版本信息字典、API应用程序实例和环境信息。
         通过调用API应用程序实例来获取版本信息,并根据返回的状态码判断是否成功获取到版本信息。
         如果状态码以"300"开头,表示成功获取到版本信息,将版本信息扩展到版本信息字典中。
        """
        tmp_versions = app(environ, self.internal_start_response)
        if self._status.startswith("300"):
            # In case of v1, app returns ClosingIterator generator object,
            # whereas in case of v2, it returns list.
            # So convert it to iterator to get the versions.
            app_iter = iter(tmp_versions)
            tmp_versions = jsonutils.loads(six.next(app_iter))
            versions['versions'].extend(tmp_versions['versions'])
        return tmp_versions

    def internal_start_response(self, status, response_headers, exc_info=None):
        self._status = status
        self._response_headers = response_headers

    def __call__(self, environ, start_response):
        self._status = ''
        self._response_headers = []
        # 根据请求路径信息environ['PATH_INFO']判断请求的API版本,并根据请求路径调用相应的API应用程序实例。
        if environ['PATH_INFO'] == '/' or environ['PATH_INFO'] == '/versions':
            versions = {'versions': []}
            tmp_versions = self._append_versions_from_app(versions, self.v1,
                                                          environ)
            # Both v1 and v2 apps run auth_token middleware. So simply
            # validate token for v1. If it fails no need to call v2 app.
            if self._status.startswith("401"):
                start_response(self._status,
                               [("Content-Type", "application/json")])
                return tmp_versions
            self._append_versions_from_app(versions, self.v2,
                                           environ)
            if len(versions['versions']):
                start_response("300 Multiple Choices",
                               [("Content-Type", "application/json")])
                return [jsonutils.dump_as_bytes(versions)]
            else:
                start_response("204 No Content", [])
                return []
        else:
            # 如果请求路径以/v1开头,则调用v1应用程序实例；否则调用v2应用程序实例。
            if environ['PATH_INFO'].startswith('/v1'):
                return self.v1(environ, start_response)
            return self.v2(environ, start_response)

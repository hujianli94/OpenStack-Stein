# Copyright (c) 2014 Bull.
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
代码的主要功能：这段代码定义了一个Blazar API的根控制器RootController，用于处理API根路径和版本路径的请求。

具体功能：
当客户端访问API根路径时，index方法会被调用，返回可用的API版本信息。
当客户端访问/versions路径时，versions方法会被调用，它实际调用了index方法，同样返回可用的API版本信息。
私有方法_append_versions_from_controller用于从指定的控制器中获取版本信息，并添加到版本列表中，返回给客户端的版本信息中包括了每个版本的链接信息。
"""

from oslo_serialization import jsonutils
import pecan

from blazar.api.v2 import controllers


class RootController(object):

    v2 = controllers.V2Controller()

    def _append_versions_from_controller(self, versions, controller, path):
        for version in getattr(controller, 'versions', None):
            version['links'] = [{
                "href": "{0}/{1}".format(pecan.request.host_url, path),
                "rel": "self"}]
            versions.append(version)

    @pecan.expose(content_type='application/json')
    def index(self):
        pecan.response.status_code = 300
        pecan.response.content_type = 'application/json'
        versions = {"versions": []}
        self._append_versions_from_controller(versions['versions'],
                                              self.v2, 'v2')
        return jsonutils.dump_as_bytes(versions)

    @pecan.expose(content_type='application/json')
    def versions(self):
        return self.index()

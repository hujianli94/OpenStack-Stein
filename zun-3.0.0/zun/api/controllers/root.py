#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""
主要目的是提供对OpenStack Zun API的版本管理功能。
它定义了API版本信息的表示方式,并实现了API根节点的控制器,能够返回API的基本信息,包括支持的版本和默认版本。

特别地,它还能够处理对API根节点的请求,当请求中没有指定API版本时,会自动重定向到默认版本。
这有助于用户在访问API时无需关心具体的版本号,只需访问根节点即可。
"""
import pecan
from pecan import rest

from zun.api.controllers import base
from zun.api.controllers import link
from zun.api.controllers import v1
from zun.api.controllers import versions

# Version类继承自base.APIBase，用于表示API的版本信息。
class Version(base.APIBase):
    """An API version representation."""
    # 定义了该类的属性列表
    fields = (
        'id',
        'links',
        'status',
        'max_version',
        'min_version'
    )

    # 用于创建一个Version对象，并根据输入参数填充该对象的属性，包括生成指向该版本API的链接。
    @staticmethod
    def convert(id, status, max, min):
        version = Version()
        version.id = id
        version.links = [link.make_link('self', pecan.request.host_url,
                                        id, '', bookmark=True)]
        version.status = status
        version.max_version = max
        version.min_version = min
        return version

# Root类也继承自base.APIBase，用于表示API根节点的信息。
class Root(base.APIBase):

    fields = (
        'name',
        'description',
        'versions',
        'default_version',
    )

    @staticmethod
    def convert():
        root = Root()
        root.name = "OpenStack Zun API"
        root.description = ("Zun is an OpenStack project which aims to "
                            "provide containers service.")

        root.versions = [Version.convert('v1', "CURRENT",
                                         versions.CURRENT_MAX_VER,
                                         versions.BASE_VER)]
        root.default_version = Version.convert('v1', "CURRENT",
                                               versions.CURRENT_MAX_VER,
                                               versions.BASE_VER)
        return root


class RootController(rest.RestController):
    # 类的_versions属性是一个包含所有支持版本的列表，当前仅支持v1版本。
    _versions = ['v1']
    """All supported API versions"""
    # _default_version属性定义了API的默认版本，即v1。
    _default_version = 'v1'
    """The default API version"""

    # v1属性是一个v1版本的控制器，用于处理v1版本的API请求。
    v1 = v1.Controller()

    # 当用户访问API根节点时，该方法会被调用，并返回API根节点的信息，格式为JSON。
    @pecan.expose('json')
    def get(self):
        # NOTE: The reason why convert() it's being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return Root.convert()

    # 如果请求的URL中没有指定API版本，该方法会将请求重定向到API的默认版本。
    @pecan.expose()
    def _route(self, args):
        """Overrides the default routing behavior.

        It redirects the request to the default version of the zun API
        if the version number is not specified in the url.
        """

        if args[0] and args[0] not in self._versions:
            args = [self._default_version] + args
        return super(RootController, self)._route(args)

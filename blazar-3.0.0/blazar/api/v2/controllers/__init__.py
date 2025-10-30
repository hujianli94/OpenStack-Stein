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

"""Version 2 of the API.

主要功能是实现Blazar项目中API版本2的根控制器,负责动态加载和管理API扩展,并根据路由参数正确地映射到相应的控制器实例。

通过这种方式,Blazar的API可以根据配置灵活地扩展功能,同时保持了代码的清晰和可维护性。
"""

from oslo_config import cfg
from oslo_log import log as logging
import pecan
from pecan import rest
from stevedore import enabled

from blazar import exceptions
from blazar.i18n import _

LOG = logging.getLogger(__name__)

# 定义了一个名为api_opts的列表,用于配置API版本2的扩展控制器。
# api_v2_controllers: 配置API版本2的扩展控制器列表。
# 默认值为['oshosts', 'leases']，表示默认加载主机和租赁控制器。
api_opts = [
    cfg.ListOpt('api_v2_controllers',
                default=['oshosts', 'leases'],
                help='API extensions to use'),
]

CONF = cfg.CONF
CONF.register_opts(api_opts, 'api')


class V2Controller(rest.RestController):
    """Version 2 API controller root."""

    versions = [{"id": "v2.0", "status": "CURRENT"}]
    _routes = {}

    # 记录未加载的插件名称
    def _log_missing_plugins(self, names):
        for name in names:
            if name not in self.extension_manager.names():
                LOG.error("API Plugin %s was not loaded", name)

    def __init__(self):
        """
        初始化V2Controller实例。
        使用stevedore.enabled.EnabledExtensionManager动态加载API扩展,check_func 参数指定过滤条件,
        只加载在CONF.api.api_v2_controllers列表中的扩展。
        加载扩展时,会调用每个扩展的obj.name属性,作为属性名添加到V2Controller实例中,
        并更新路由信息。

        [entry_points]
        blazar.api.v2.controllers.extensions =
            oshosts=blazar.api.v2.controllers.extensions.host:HostsController
            leases=blazar.api.v2.controllers.extensions.lease:LeasesController
        """
        extensions = []

        self.extension_manager = enabled.EnabledExtensionManager(
            check_func=lambda ext: ext.name in CONF.api.api_v2_controllers,
            namespace='blazar.api.v2.controllers.extensions',
            invoke_on_load=True
        )
        self._log_missing_plugins(CONF.api.api_v2_controllers)
        # 遍历加载的扩展,将扩展名作为属性添加到V2Controller实例中,并更新路由信息。
        for ext in self.extension_manager.extensions:
            try:
                setattr(self, ext.obj.name, ext.obj)
            except TypeError:
                raise exceptions.BlazarException(
                    _("API name must be specified for "
                        "extension {0}").format(ext.name))
            self._routes.update(ext.obj.extra_routes)
            extensions.append(ext.obj.name)
        # 记录已加载的扩展名称。
        LOG.debug("Loaded extensions: {0}".format(extensions))

    @pecan.expose()
    def _route(self, args):
        """Overrides the default routing behavior.

        It allows to map controller URL with correct controller instance.
        By default, it maps with the same name.

        重写了pecan.rest.RestController的_route方法。
        根据传入的路由参数args,从_routes字典中获取对应的路由,
        如果路由不存在则将其重定向到一个不存在的控制器('http404-nonexistingcontroller')。
        处理IndexError异常,当没有传入路由参数时,记录错误信息。
        """

        try:
            route = self._routes.get(args[0], args[0])
            if route is None:
                # NOTE(sbauza): Route must map to a non-existing controller
                args[0] = 'http404-nonexistingcontroller'
            else:
                args[0] = route
        except IndexError:
            LOG.error("No args found on V2 controller")
        return super(V2Controller, self)._route(args)

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
这段代码定义了几个Pecan Hook类,用于在处理请求的过程中附加一些必要的对象到请求上下文中,以便控制器可以方便地访问这些对象。
"""
from oslo_config import cfg
from oslo_log import log as logging
from pecan import hooks

from blazar.api import context
from blazar.db import api as dbapi
from blazar.manager.leases import rpcapi as leases_rpcapi
from blazar.manager.oshosts import rpcapi as hosts_rpcapi

LOG = logging.getLogger(__name__)

# 在请求处理之前，将全局配置对象 cfg.CONF 附加到请求对象上，使得控制器能够访问配置信息。
class ConfigHook(hooks.PecanHook):
    """ConfigHook

    Attach the configuration object to the request
    so controllers can get to it.
    """

    def before(self, state):
        state.request.cfg = cfg.CONF

# 在请求处理之前，获取数据库API的实例并附加到请求对象上，使得控制器能够访问数据库。
class DBHook(hooks.PecanHook):
    """Attach the dbapi object to the request so controllers can get to it."""

    def before(self, state):
        state.request.dbapi = dbapi.get_instance()

# 在请求处理之前，从请求头中创建请求上下文对象并附加到请求对象上，使得控制器能够访问请求的上下文信息。
# 在请求处理完成后（无论是否发生错误），确保上下文对象正确退出，释放相关资源。
class ContextHook(hooks.PecanHook):
    """Configures a request context and attaches it to the request."""

    def before(self, state):
        state.request.context = context.ctx_from_headers(state.request.headers)
        state.request.context.__enter__()

    # NOTE(sbauza): on_error() can be fired before after() if the original
    #               exception is not catched by WSME. That's necessary to not
    #               handle context.__exit__() within on_error() as it could
    #               lead to pop the stack twice for the same request
    def after(self, state):
        # If no API extensions are loaded, context is empty
        if state.request.context:
            state.request.context.__exit__(None, None, None)

# 在请求处理之前，创建租赁管理器和主机管理器的RPC API实例并附加到请求对象上，使得控制器能够调用这些服务。
class RPCHook(hooks.PecanHook):
    """Attach the rpcapi object to the request so controllers can get to it."""

    def before(self, state):
        state.request.rpcapi = leases_rpcapi.ManagerRPCAPI()
        state.request.hosts_rpcapi = hosts_rpcapi.ManagerRPCAPI()

# Copyright (c) 2013 Bull.
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
ManagerRPCAPI 类的主要功能是提供与 Blazar 管理器服务进行 RPC 通信的方法。
它封装了对计算主机资源的 CRUD 操作（创建、读取、更新、删除），以及查询分配信息的操作。

RPC 方法实现：
    get_computehost: 获取指定计算主机的详细信息。
    list_computehosts: 列出所有计算主机的信息，可以接受查询参数以过滤结果。
    create_computehost: 根据传入的参数创建一个新的计算主机。
    update_computehost: 更新指定计算主机的信息，传入要更新的参数字典。
    delete_computehost: 删除指定的计算主机。
    list_allocations: 列出所有计算主机上的分配信息，可以接受查询参数以过滤结果。
    get_allocations: 列出指定计算主机上的分配信息，可以接受查询参数以过滤结果
这些操作使得其他服务能够通过 RPC 调用来管理 Blazar 中的计算主机资源。
"""

from oslo_config import cfg

from blazar import manager
from blazar.utils import service

CONF = cfg.CONF
CONF.import_opt('rpc_topic', 'blazar.manager.service', 'manager')


class ManagerRPCAPI(service.RPCClient):
    """Client side for the Manager RPC API.

    Used from other services to communicate with blazar-manager service.
    """
    BASE_RPC_API_VERSION = '1.0'

    def __init__(self):
        """Initiate RPC API client with needed topic and RPC version."""
        super(ManagerRPCAPI, self).__init__(manager.get_target())

    def get_computehost(self, host_id):
        """Get detailed info about some computehost."""
        return self.call('physical:host:get_computehost', host_id=host_id)

    def list_computehosts(self, query=None):
        """List all computehosts."""
        return self.call('physical:host:list_computehosts', query=query)

    def create_computehost(self, host_values):
        """Create computehost with specified parameters."""
        return self.call('physical:host:create_computehost',
                         host_values=host_values)

    def update_computehost(self, host_id, values):
        """Update computehost with passes values dictionary."""
        return self.call('physical:host:update_computehost', host_id=host_id,
                         values=values)

    def delete_computehost(self, host_id):
        """Delete specified computehost."""
        return self.call('physical:host:delete_computehost',
                         host_id=host_id)

    def list_allocations(self, query):
        """List all allocations on all computehosts."""
        return self.call('physical:host:list_allocations', query=query)

    def get_allocations(self, host_id, query):
        """List all allocations on a specified computehost."""
        return self.call('physical:host:get_allocations',
                         host_id=host_id, query=query)

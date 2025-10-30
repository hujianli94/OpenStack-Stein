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
代码实现了一个RESTful API接口,主要用于Blazar租赁的CRUD(创建、读取、更新、删除)操作。

通过定义不同的路由和处理函数,使得外部应用可以通过HTTP请求对Blazar中的租赁资源进行管理和查询。

同时,代码中还包含了一个获取所有可用插件的接口,这些插件可以扩展Blazar的功能。
"""

from oslo_log import log as logging

from blazar.api.v1.leases import service
from blazar.api.v1 import utils as api_utils
from blazar.api.v1 import validation
from blazar import utils

LOG = logging.getLogger(__name__)


def get_rest():
    """Return Rest app"""
    return rest


rest = api_utils.Rest('v1_0', __name__, url_prefix='/v1')
_api = utils.LazyProxy(service.API)


# Leases operations

@rest.get('/leases', query=True)
def leases_list(query):
    """List all existing leases."""
    return api_utils.render(leases=_api.get_leases(query))


@rest.post('/leases')
def leases_create(data):
    """Create new lease."""
    return api_utils.render(lease=_api.create_lease(data))


@rest.get('/leases/<lease_id>')
@validation.check_exists(_api.get_lease, lease_id='lease_id')
def leases_get(lease_id):
    """Get lease by its ID."""
    return api_utils.render(lease=_api.get_lease(lease_id))


@rest.put('/leases/<lease_id>')
@validation.check_exists(_api.get_lease, lease_id='lease_id')
def leases_update(lease_id, data):
    """Update lease."""
    return api_utils.render(lease=_api.update_lease(lease_id, data))


@rest.delete('/leases/<lease_id>')
@validation.check_exists(_api.get_lease, lease_id='lease_id')
def leases_delete(lease_id):
    """Delete specified lease."""
    _api.delete_lease(lease_id)
    return api_utils.render()


# Plugins operations

@rest.get('/plugins')
def plugins_list():
    """List all possible plugins."""
    return api_utils.render(plugins=_api.get_plugins())

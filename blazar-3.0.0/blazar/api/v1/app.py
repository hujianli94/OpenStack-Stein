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
主要功能是构建Blazar REST API v1 应用程序，处理身份验证，路由请求到适当的处理函数，并能够根据配置动态加载扩展。

同时，它还包括了详细的错误处理机制和可选的请求/响应记录功能。
"""
import eventlet
eventlet.monkey_patch(
    os=True, select=True, socket=True, thread=True, time=True)

import flask
from keystonemiddleware import auth_token
from oslo_config import cfg
from oslo_log import log as logging
from oslo_middleware import debug
from stevedore import enabled
from werkzeug import exceptions as werkzeug_exceptions

from blazar.api.v1 import utils as api_utils


LOG = logging.getLogger(__name__)

CONF = cfg.CONF
# 从配置文件中导入log_exchange选项，用于决定是否记录请求和响应的详细信息。
CONF.import_opt('log_exchange', 'blazar.config')


# 定义一个函数来处理HTTP异常，并将异常信息以JSON格式返回给客户端。
# 如果异常是werkzeug_exceptions.HTTPException类型，则直接使用其状态码和描述；否则，将其视为服务器错误（500），并返回默认的错误信息。
def make_json_error(ex):
    if isinstance(ex, werkzeug_exceptions.HTTPException):
        status_code = ex.code
        description = ex.description
    else:
        status_code = 500
        description = str(ex)
    return api_utils.render({'error': status_code,
                             'error_message': description},
                            status=status_code)

# 定义一个路由处理函数，当客户端访问根路径/或/versions时，返回当前支持的API版本信息。
# 这里只支持一个版本v1.0，状态为CURRENT，并附带指向该版本API的URL链接。
def version_list():
    return api_utils.render({
        "versions": [
            {"id": "v1.0",
             "status": "CURRENT",
             "links": [{"href": "{0}v1".format(flask.request.host_url),
                        "rel": "self"}]
             },
        ],
    }, status="300 Multiple Choices")

# 创建应用,定义了一个函数用于构建和返回Blazar API的WSGI应用程序。
def make_app():
    """App builder (wsgi).

    Entry point for Blazar REST API server.
    """
    app = flask.Flask('blazar.api')
    # 使用app.route装饰器注册根路径和版本路径的路由处理函数为version_list。
    app.route('/', methods=['GET'])(version_list)
    app.route('/versions', methods=['GET'])(version_list)

    LOG.debug("List of plugins: %s", cfg.CONF.manager.plugins)

    # 创建一个EnabledExtensionManager实例，用于动态加载扩展。它会根据配置文件中的manager.plugins选项和预定义的leases插件来决定哪些扩展需要加载。
    """
    [entry_points]
    blazar.api.v1.extensions =
        leases=blazar.api.v1.leases.v1_0:get_rest
        physical.host.plugin=blazar.api.v1.oshosts.v1_0:get_rest
        virtual.floatingip.plugin=blazar.api.v1.floatingips.v1_0:get_rest
    """
    plugins = cfg.CONF.manager.plugins + ['leases']
    extension_manager = enabled.EnabledExtensionManager(
        check_func=lambda ext: ext.name in plugins,
        namespace='blazar.api.v1.extensions',
        invoke_on_load=False
        )
    # 遍历所有加载的扩展，并将它们的蓝图（Blueprint）注册到Flask应用中。
    for ext in extension_manager.extensions:
        bp = ext.plugin()
        app.register_blueprint(bp, url_prefix=bp.url_prefix)
    # 注册所有的HTTP异常处理函数为make_json_error，以便在发生异常时返回统一格式的错误信息。
    for code in werkzeug_exceptions.default_exceptions:
        app.register_error_handler(code, make_json_error)

    # 根据配置，决定是否启用调试中间件oslo_middleware.debug.Debug来记录请求和响应的详细信息。
    if cfg.CONF.debug and not cfg.CONF.log_exchange:
        LOG.debug('Logging of request/response exchange could be enabled '
                  'using flag --log_exchange')

    if cfg.CONF.log_exchange:
        app.wsgi_app = debug.Debug.factory(app.config)(app.wsgi_app)
    # 注册keystonemiddleware.auth_token作为身份验证中间件，用于处理身份验证请求。
    app.wsgi_app = auth_token.filter_factory(app.config)(app.wsgi_app)

    return app  # 返回构建好的WSGI应用程序。

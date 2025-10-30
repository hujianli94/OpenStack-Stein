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
主要功能是配置和创建Blazar API v2版本的应用程序。
它通过注册配置选项来管理身份验证策略和日志记录,并使用Pecan框架创建了一个WSGI应用程序实例。
在创建过程中，它添加了几个关键的中间件来处理身份验证、错误处理和调试。
"""

from keystonemiddleware import auth_token
from oslo_config import cfg
from oslo_middleware import debug
import pecan

from blazar.api.v2 import hooks
from blazar.api.v2 import middleware

# 定义了一个配置选项列表，其中包含一个字符串类型的配置选项auth_strategy。
# 该选项用于指定Blazar API v2版本的身份验证策略，默认值为'keystone'，表示使用Keystone进行身份验证。
auth_opts = [
    cfg.StrOpt('auth_strategy',
               default='keystone',
               help='The strategy to use for auth: noauth or keystone.'),
]

CONF = cfg.CONF
CONF.register_opts(auth_opts)

CONF.import_opt('log_exchange', 'blazar.config')

OPT_GROUP_NAME = 'keystone_authtoken'

# 定义了一个名为setup_app的函数，用于设置Blazar API v2应用程序。
# 该函数接受两个可选参数：pecan_config（Pecan配置对象）和extra_hooks（额外的钩子列表）。
def setup_app(pecan_config=None, extra_hooks=None):
    # 创建一个包含多个钩子的列表app_hooks，这些钩子用于在处理请求时执行某些操作，
    # 例如配置管理、数据库操作、上下文管理、RPC（远程过程调用）等。
    app_hooks = [hooks.ConfigHook(),
                 hooks.DBHook(),
                 hooks.ContextHook(),
                 hooks.RPCHook(),
                 ]
    # TODO(sbauza): Add stevedore extensions for loading hooks
    # 如果提供了额外的钩子列表extra_hooks，则将其添加到app_hooks列表中。
    if extra_hooks:
        app_hooks.extend(extra_hooks)
    # 使用pecan.make_app函数创建一个Pecan应用程序实例。
    app = pecan.make_app(
        pecan_config.app.root,  # 指定应用程序的根控制器路径。
        debug=CONF.debug,       # 根据配置选项debug的值决定是否启用调试模式。
        hooks=app_hooks,        # 将之前创建的钩子列表app_hooks传递给Pecan应用程序。
        wrap_app=middleware.ParsableErrorMiddleware,    #指定一个中间件来包装应用程序，该中间件用于处理可解析的错误。
        guess_content_type_from_ext=False   # 禁用根据文件扩展名猜测内容类型的选项。
    )

    # WSGI middleware for Keystone auth
    # NOTE(sbauza): ACLs are always active unless for unittesting where
    #               enable_acl could be set to False
    # 如果配置选项enable_acl为True，则将auth_token.AuthProtocol中间件添加到应用程序中，用于处理Keystone认证。
    # ACL（访问控制列表）在这种情况下始终处于活动状态，除非是在进行单元测试时将其禁用。
    if pecan_config.app.enable_acl:
        app = auth_token.AuthProtocol(app, {})

    return app  # 返回创建的Pecan应用程序实例

# 定义了一个名为make_app的函数，用于创建Blazar API v2应用程序。
def make_app():
    # 创建一个配置字典config，用于指定应用程序的相关配置。
    config = {
        'app': {
            'modules': ['blazar.api.v2'],             # 指定应用程序的模块路径列表，这里只包含一个模块路径blazar.api.v2。
            'root': 'blazar.api.root.RootController', # 指定应用程序的根控制器路径
            'enable_acl': True,                       # 启用ACL（访问控制列表），用于控制对API的访问。
        }
    }
    # 使用pecan.load_app函数加载配置字典，并创建Pecan应用程序实例。
    app = pecan.load_app(config)
    # WSGI middleware for debugging
    # NOTE(sbauza): Fill Pecan config and call modules' path app.setup_app()
    app = pecan.load_app(config)
    # WSGI middleware for debugging
    # 如果配置选项log_exchange为True，则将debug.Debug.factory中间件添加到应用程序中，用于调试目的。
    if CONF.log_exchange:
        app = debug.Debug.factory(config)(app)
    return app  # 返回创建的Pecan应用程序实例

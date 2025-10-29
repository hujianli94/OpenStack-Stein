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
它通过注册配置选项来管理身份验证策略和日志记录，并使用Pecan框架创建了一个WSGI应用程序实例。
在创建过程中，它添加了几个关键的中间件来处理身份验证、错误处理和调试。

"""

from keystonemiddleware import auth_token
from oslo_config import cfg
from oslo_middleware import debug
import pecan

from blazar.api.v2 import hooks
from blazar.api.v2 import middleware


auth_opts = [
    cfg.StrOpt('auth_strategy',
               default='keystone',
               help='The strategy to use for auth: noauth or keystone.'),
]

CONF = cfg.CONF
CONF.register_opts(auth_opts)

CONF.import_opt('log_exchange', 'blazar.config')

OPT_GROUP_NAME = 'keystone_authtoken'


def setup_app(pecan_config=None, extra_hooks=None):

    app_hooks = [hooks.ConfigHook(),
                 hooks.DBHook(),
                 hooks.ContextHook(),
                 hooks.RPCHook(),
                 ]
    # TODO(sbauza): Add stevedore extensions for loading hooks
    if extra_hooks:
        app_hooks.extend(extra_hooks)

    app = pecan.make_app(
        pecan_config.app.root,
        debug=CONF.debug,
        hooks=app_hooks,
        wrap_app=middleware.ParsableErrorMiddleware,
        guess_content_type_from_ext=False
    )

    # WSGI middleware for Keystone auth
    # NOTE(sbauza): ACLs are always active unless for unittesting where
    #               enable_acl could be set to False
    if pecan_config.app.enable_acl:
        app = auth_token.AuthProtocol(app, {})

    return app


def make_app():
    config = {
        'app': {
            'modules': ['blazar.api.v2'],
            'root': 'blazar.api.root.RootController',
            'enable_acl': True,
        }
    }
    # NOTE(sbauza): Fill Pecan config and call modules' path app.setup_app()
    app = pecan.load_app(config)
    # WSGI middleware for debugging
    if CONF.log_exchange:
        app = debug.Debug.factory(config)(app)
    return app

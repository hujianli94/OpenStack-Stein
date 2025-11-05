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
主要功能是设置和加载Zun API的应用程序。

- get_pecan_config函数获取Pecan的配置信息
- setup_app函数创建并返回一个Pecan应用实例
- load_app函数则根据配置文件路径加载并返回一个WSGI应用程序
- app_factory作为工厂函数,方便在其他模块中调用以创建应用实例。
"""
import os

from oslo_config import cfg
from oslo_log import log
from paste import deploy
import pecan

from zun.api import config as api_config
from zun.api import middleware
from zun.common import config as common_config
import zun.conf

CONF = zun.conf.CONF
LOG = log.getLogger(__name__)

# 该函数用于从文件中获取Pecan的配置信息。它首先处理文件名，
# 将可能存在的.pyc后缀替换为.py，然后使用pecan.configuration.conf_from_file函数从指定的Python文件中读取配置信息。
def get_pecan_config():
    # Set up the pecan configuration
    filename = api_config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)

# 根据传入的配置或默认配置设置并返回一个Pecan应用实例。
def setup_app(config=None):
    if not config:
        config = get_pecan_config()

    app_conf = dict(config.app)
    common_config.set_config_defaults()

    app = pecan.make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        wrap_app=middleware.ParsableErrorMiddleware,
        **app_conf
    )

    return app

# 负责加载并返回一个WSGI应用程序。
def load_app():
    cfg_file = None
    cfg_path = CONF.api.api_paste_config
    if not os.path.isabs(cfg_path):
        cfg_file = CONF.find_file(cfg_path)
    elif os.path.exists(cfg_path):
        cfg_file = cfg_path

    if not cfg_file:
        raise cfg.ConfigFilesNotFoundError([CONF.api.api_paste_config])
    LOG.info("Full WSGI config used: %s", cfg_file)
    return deploy.loadapp("config:" + cfg_file)

# 这是一个工厂函数，用于创建和返回一个Pecan应用实例。它直接调用了setup_app()函数，并将返回的Pecan应用实例作为结果返回。
def app_factory(global_config, **local_conf):
    return setup_app()

# Copyright 2013 - Noorul Islam K M
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from zun.api import hooks

# Pecan Application Configurations
app = {
    'root': 'zun.api.controllers.root.RootController', # 定义WSGI应用的根控制器
    'modules': ['zun'],                                # 定义WSGI应用的模块列表
    'hooks': [
        hooks.ContextHook(),
        hooks.NoExceptionTracebackHook(),
        hooks.RPCHook(),
    ],
    'debug': False,
}

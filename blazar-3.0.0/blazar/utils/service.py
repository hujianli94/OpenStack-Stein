#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright © 2013  Julien Danjou <julien@danjou.info>
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
"""
这段代码的主要功能是通过定义RPC客户端和服务器类,实现Blazar服务之间的通信。

ContextEndpointHandler类用于在处理请求时管理上下文环境,确保请求处理过程中所需的环境信息正确无误。

with_empty_context装饰器则为某些函数提供一个空的上下文环境。最后,prepare_service函数用于初始化整个服务,设置日志配置。
"""

import functools

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_service import service

from blazar import context

LOG = logging.getLogger(__name__)

# 创建一个RPC客户端，用于向Blazar服务发送请求。
class RPCClient(object):
    def __init__(self, target):
        super(RPCClient, self).__init__()
        self._client = messaging.RPCClient(
            target=target,
            transport=messaging.get_rpc_transport(cfg.CONF),
        )

    def cast(self, name, **kwargs):
        ctx = context.current()
        self._client.cast(ctx.to_dict(), name, **kwargs)

    def call(self, name, **kwargs):
        ctx = context.current()
        return self._client.call(ctx.to_dict(), name, **kwargs)

# 创建一个RPC服务器，用于接收并处理来自客户端的消息。
class RPCServer(service.Service):
    def __init__(self, target):
        super(RPCServer, self).__init__()
        self._server = messaging.get_rpc_server(
            target=target,
            transport=messaging.get_rpc_transport(cfg.CONF),
            endpoints=[ContextEndpointHandler(self, target)],
            executor='eventlet',
        )

    def start(self):
        super(RPCServer, self).start()
        self.tg.add_thread(self._server.start)

    def stop(self):
        super(RPCServer, self).stop()
        self._server.stop()

# 在处理RPC请求时，管理请求的上下文环境。
class ContextEndpointHandler(object):
    def __init__(self, endpoint, target):
        self.__endpoint = endpoint
        self.target = target

    def __getattr__(self, name):
        try:
            method = getattr(self.__endpoint, name)

            def run_method(__ctx, **kwargs):
                with context.BlazarContext(**__ctx):
                    return method(**kwargs)

            return run_method
        except AttributeError:
            LOG.error("No %(method)s method found implemented in "
                      "%(class)s class",
                      {'method': name, 'class': self.__endpoint})

# 为某些函数提供一个空的上下文环境。
def with_empty_context(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        with context.BlazarContext():
            return func(*args, **kwargs)

    return decorator

# 初始化服务，设置日志配置。
def prepare_service(argv=[]):
    logging.setup(cfg.CONF, 'blazar')

# Copyright 2011 OpenStack Foundation
# Copyright 2011 Justin Santa Barbara
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import importutils
import webob.dec
import webob.exc

import cinder.api.openstack
from cinder.api.openstack import wsgi
from cinder import exception
import cinder.policy


CONF = cfg.CONF

LOG = logging.getLogger(__name__)
FILES_TO_SKIP = ['resource_common_manage.py', 'scheduler_hints.py']

# ExtensionDescriptor 是一个扩展的基类，定义了扩展应该实现的方法。
class ExtensionDescriptor(object):
    """Base class that defines the contract for extensions.

    Note that you don't have to derive from this class to have a valid
    extension; it is purely a convenience.

    """

    # The name of the extension, e.g., 'Fox In Socks'
    name = None

    # The alias for the extension, e.g., 'FOXNSOX'
    alias = None

    # The timestamp when the extension was last updated, e.g.,
    # '2011-01-22T13:25:27-06:00'
    updated = None

    def __init__(self, ext_mgr):
        """Register extension with the extension manager."""

        ext_mgr.register(self)
        self.ext_mgr = ext_mgr

    # 返回一个扩展资源的列表。扩展资源是新的名词，并且可以通过URL访问。
    def get_resources(self):
        """List of extensions.ResourceExtension extension objects.

        Resources define new nouns, and are accessible through URLs.

        """
        resources = []
        return resources
    # 返回一个控制器扩展的列表。控制器扩展用于扩展现有的控制器。
    def get_controller_extensions(self):
        """List of extensions.ControllerExtension extension objects.

        Controller extensions are used to extend existing controllers.
        """
        controller_exts = []
        return controller_exts

# ExtensionsResource 类用于处理与扩展相关的API请求。
class ExtensionsResource(wsgi.Resource):

    def __init__(self, extension_manager):
        self.extension_manager = extension_manager
        super(ExtensionsResource, self).__init__(None)

    def _translate(self, ext):
        ext_data = {}
        ext_data['name'] = ext.name
        ext_data['alias'] = ext.alias
        ext_data['description'] = ext.__doc__
        ext_data['updated'] = ext.updated
        ext_data['links'] = []  # TODO(dprince): implement extension links
        return ext_data

    def index(self, req):
        extensions = []
        for _alias, ext in self.extension_manager.extensions.items():
            extensions.append(self._translate(ext))
        return dict(extensions=extensions)

    def show(self, req, id):
        try:
            # NOTE(dprince): the extensions alias is used as the 'id' for show
            ext = self.extension_manager.extensions[id]
        except KeyError:
            raise webob.exc.HTTPNotFound()

        return dict(extension=self._translate(ext))

    def delete(self, req, id):
        raise webob.exc.HTTPNotFound()

    def create(self, req):
        raise webob.exc.HTTPNotFound()


# ExtensionManager 类负责从配置路径加载扩展，并管理扩展的注册和查询。
class ExtensionManager(object):
    """Load extensions from the configured extension path.

    See cinder/tests/api/extensions/foxinsocks/extension.py for an
    example extension implementation.

    """

    def __init__(self):
        LOG.debug('Initializing extension manager.')

        self.cls_list = CONF.osapi_volume_extension
        self.extensions = {}
        self._load_extensions()

    def is_loaded(self, alias):
        return alias in self.extensions

    def register(self, ext):
        # Do nothing if the extension doesn't check out
        if not self._check_extension(ext):
            return

        alias = ext.alias
        LOG.debug('Loaded extension: %s', alias)

        if alias in self.extensions:
            raise exception.Error("Found duplicate extension: %s" % alias)
        self.extensions[alias] = ext

    def get_resources(self):
        """Returns a list of ResourceExtension objects."""

        resources = []
        resources.append(ResourceExtension('extensions',
                                           ExtensionsResource(self)))

        for ext in self.extensions.values():
            try:
                resources.extend(ext.get_resources())
            except AttributeError:
                # NOTE(dprince): Extension aren't required to have resource
                # extensions
                pass
        return resources

    def get_controller_extensions(self):
        """Returns a list of ControllerExtension objects."""
        controller_exts = []
        for ext in self.extensions.values():
            try:
                get_ext_method = ext.get_controller_extensions
            except AttributeError:
                # NOTE(Vek): Extensions aren't required to have
                # controller extensions
                continue
            controller_exts.extend(get_ext_method())
        return controller_exts

    def _check_extension(self, extension):
        """Checks for required methods in extension objects."""
        try:
            LOG.debug('Ext name: %s', extension.name)
            LOG.debug('Ext alias: %s', extension.alias)
            LOG.debug('Ext description: %s',
                      ' '.join(extension.__doc__.strip().split()))
            LOG.debug('Ext updated: %s', extension.updated)
        except AttributeError:
            LOG.exception("Exception loading extension.")
            return False

        return True

    def load_extension(self, ext_factory):
        """Execute an extension factory.

        Loads an extension.  The 'ext_factory' is the name of a
        callable that will be imported and called with one
        argument--the extension manager.  The factory callable is
        expected to call the register() method at least once.
        """

        LOG.debug("Loading extension %s", ext_factory)

        # Load the factory
        factory = importutils.import_class(ext_factory)

        # Call it
        LOG.debug("Calling extension factory %s", ext_factory)
        factory(self)

    def _load_extensions(self):
        """Load extensions specified on the command line."""

        extensions = list(self.cls_list)

        for ext_factory in extensions:
            try:
                self.load_extension(ext_factory)
            except Exception as exc:
                LOG.warning('Failed to load extension %(ext_factory)s: '
                            '%(exc)s',
                            {'ext_factory': ext_factory, 'exc': exc})


# 用于扩展OpenStack Cinder API的核心控制器。
class ControllerExtension(object):
    """Extend core controllers of cinder OpenStack API.

    Provide a way to extend existing cinder OpenStack API core
    controllers.
    """

    def __init__(self, extension, collection, controller):
        self.extension = extension
        self.collection = collection
        self.controller = controller

# 用于向OpenStack Cinder API添加顶级资源。
class ResourceExtension(object):
    """Add top level resources to the OpenStack API in cinder."""

    def __init__(self, collection, controller, parent=None,
                 collection_actions=None, member_actions=None,
                 custom_routes_fn=None):
        if not collection_actions:
            collection_actions = {}
        if not member_actions:
            member_actions = {}
        self.collection = collection
        self.controller = controller
        self.parent = parent
        self.collection_actions = collection_actions
        self.member_actions = member_actions
        self.custom_routes_fn = custom_routes_fn


# load_standard_extensions 函数用于加载标准API扩展。
# 功能：遍历给定路径下的所有模块和子目录，尝试加载扩展类并将它们注册到扩展管理器中。
def load_standard_extensions(ext_mgr, logger, path, package, ext_list=None):
    """Registers all standard API extensions."""

    # Walk through all the modules in our directory...
    our_dir = path[0]
    for dirpath, dirnames, filenames in os.walk(our_dir):
        # Compute the relative package name from the dirpath
        relpath = os.path.relpath(dirpath, our_dir)
        if relpath == '.':
            relpkg = ''
        else:
            relpkg = '.%s' % '.'.join(relpath.split(os.sep))

        # Now, consider each file in turn, only considering .py and .pyc files
        for fname in filenames:
            root, ext = os.path.splitext(fname)

            # Skip __init__ and anything that's not .py and .pyc
            if ((ext not in ('.py', '.pyc')) or root == '__init__' or
                    fname in FILES_TO_SKIP):
                continue

            # If .pyc and .py both exist, skip .pyc
            if ext == '.pyc' and ((root + '.py') in filenames):
                continue

            # Try loading it
            classname = "%s%s" % (root[0].upper(), root[1:])
            classpath = ("%s%s.%s.%s" %
                         (package, relpkg, root, classname))

            if ext_list is not None and classname not in ext_list:
                logger.debug("Skipping extension: %s" % classpath)
                continue

            try:
                ext_mgr.load_extension(classpath)
            except Exception as exc:
                logger.warning('Failed to load extension %(classpath)s: '
                               '%(exc)s',
                               {'classpath': classpath, 'exc': exc})

        # Now, let's consider any subdirectories we may have...
        subdirs = []
        for dname in dirnames:
            # Skip it if it does not have __init__.py
            if not os.path.exists(os.path.join(dirpath, dname,
                                               '__init__.py')):
                continue

            # If it has extension(), delegate...
            ext_name = ("%s%s.%s.extension" %
                        (package, relpkg, dname))
            try:
                ext = importutils.import_class(ext_name)
            except ImportError:
                # extension() doesn't exist on it, so we'll explore
                # the directory for ourselves
                subdirs.append(dname)
            else:
                try:
                    ext(ext_mgr)
                except Exception as exc:
                    logger.warning('Failed to load extension '
                                   '%(ext_name)s: %(exc)s',
                                   {'ext_name': ext_name, 'exc': exc})

        # Update the list of directories we'll explore...
        dirnames[:] = subdirs


# extension_authorizer 函数用于生成授权检查函数。
# 功能：根据API名称和扩展名称生成一个授权检查函数，该函数可以检查给定的上下文是否有权限执行特定的操作。
def extension_authorizer(api_name, extension_name):
    def authorize(context, target=None, action=None):
        if target is None:
            target = {'project_id': context.project_id,
                      'user_id': context.user_id}
        if action is None:
            act = '%s_extension:%s' % (api_name, extension_name)
        else:
            act = '%s_extension:%s:%s' % (api_name, extension_name, action)
        cinder.policy.authorize(context, act, target)
    return authorize

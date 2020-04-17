from importlib import import_module

from cms.plugin_pool import plugin_pool

from cmsplus.app_settings import cmsplus_settings as cps

# register all plugins configured cmsplus app_settings
for plugin in cps.PLUGINS:
    mod_name, cls_name = plugin.rsplit('.', 1)
    mod = import_module(mod_name)
    cls = getattr(mod, cls_name)
    plugin_pool.register_plugin(cls)

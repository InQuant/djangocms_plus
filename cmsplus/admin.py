import json
from json import JSONDecodeError

from cms.admin.pageadmin import PageAdmin
from cms.models import Page, Placeholder, UserSettings, CMSPlugin
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils.translation import ugettext_lazy as _
from cms import api

from cmsplus.plugin_base import PlusPluginBase


def add_plugin(placeholder, plugin_data, target=None):
    _add_plugin = {
        'placeholder': placeholder,
        'plugin_type': plugin_data.get('plugin_type'),
        'language': plugin_data.get('language'),
    }
    if plugin_data.get('is_plusplugin'):
        _add_plugin['data'] = plugin_data.get('data')
    else:
        _add_plugin = {**_add_plugin, **plugin_data.get('data')}

    generated_plugin = api.add_plugin(**_add_plugin, target=target)

    # add children recursively
    for plugin in plugin_data.get('children', []):
        add_plugin(placeholder, plugin, target=generated_plugin)


class CustomPageAdmin(PageAdmin):
    def get_urls(self):
        urls = [
            path('clipboard/import', self.admin_site.admin_view(self.clipboard_import), name='clipboard-import'),
            path('clipboard/export', self.admin_site.admin_view(self.clipboard_export), name='clipboard-export'),
        ]
        return urls + super().get_urls()

    @staticmethod
    def clipboard_import(request):
        context = {'errors': []}
        if not request.user.is_staff:
            return HttpResponse(status=401)

        if request.POST:
            user_settings = UserSettings.objects.get(user=request.user)
            clipboard = Placeholder.objects.get(usersettings=user_settings, slot='clipboard')
            # clear current clipboard
            clipboard.get_plugins().delete()

            data = []
            try:
                data = json.loads(request.POST.get('json_data'))
            except JSONDecodeError:
                context['errors'].append(_('Given json could not be converted'))

            for plugin_data in data:
                add_plugin(clipboard, plugin_data)

            if len(context['errors']) < 1:
                context['success'] = True
                context['plugins'] = [p.plugin_type for p in clipboard.get_plugins()]

        return render(request, 'cmsplus/admin/clipboard_import.html', context=context)

    @staticmethod
    def clipboard_export(request):
        if not request.user.is_staff:
            return HttpResponse(status=401)

        context = {}
        placeholder = request.toolbar.clipboard
        plugins = placeholder.get_plugins()

        _plugins = []

        # restructure data
        for plugin in plugins:
            instance, p = plugin.get_plugin_instance()

            plugin_data = {
                'id': plugin.id,
                'language': plugin.language,
                'plugin_type': plugin.plugin_type,
                'parent_id': plugin.parent_id,
                'children': [],
                'depth': plugin.depth,
            }

            # handle PlusPlugins
            if issubclass(p.__class__, PlusPluginBase):
                plugin_data['data'] = instance._json
                plugin_data['is_plusplugin'] = True

            # handle django cms plugins
            else:
                plugin_fields = p.form.base_fields
                data = {}
                for field in plugin_fields:
                    data[field] = getattr(instance, field)
                plugin_data['data'] = data

            _plugins.append(plugin_data)

        # generate plugin tree (set children)
        _plugins = sorted(_plugins, key=lambda k: k['depth'], reverse=True)
        plugin_tree = []
        for current_plugin in _plugins:
            if not current_plugin.get('parent_id'):
                plugin_tree.append(current_plugin)
                continue

            for plugin in _plugins:
                if current_plugin.get('parent_id') == plugin.get('id'):
                    plugin['children'].append(current_plugin)

        context['content'] = json.dumps(plugin_tree)
        return render(request, 'cmsplus/admin/clipboard_export.html', context=context)


admin.site.unregister(Page)
admin.site.register(Page, CustomPageAdmin)

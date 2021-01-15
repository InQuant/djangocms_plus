import json
from json import JSONDecodeError

from cms.admin.pageadmin import PageAdmin
from cms.models import Page, Placeholder, UserSettings
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils.translation import ugettext_lazy as _

from cmsplus.utils import generate_plugin_tree
from cmsplus.utils import plus_add_plugin


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
                plus_add_plugin(clipboard, plugin_data)

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
        plugin_tree = generate_plugin_tree(placeholder)

        context['content'] = json.dumps(plugin_tree)
        return render(request, 'cmsplus/admin/clipboard_export.html', context=context)


admin.site.unregister(Page)
admin.site.register(Page, CustomPageAdmin)

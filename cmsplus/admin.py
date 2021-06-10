import json
from json import JSONDecodeError

from adminsortable2.admin import SortableAdminMixin
from cms.admin.pageadmin import PageAdmin
from cms.models import Page, Placeholder, UserSettings
from django import forms
from django.contrib import admin
from django.core.files.temp import NamedTemporaryFile
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils.translation import ugettext_lazy as _

from cmsplus.fields import SCSSEditor
from cmsplus.models import SiteStyle
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


class SiteStyleForm(forms.ModelForm):
    content = forms.CharField(widget=SCSSEditor)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.file:
            self.fields['content'].initial = self.get_from_file()

    def get_from_file(self):
        self.instance.file.open('r')
        content = self.instance.file.read()
        self.instance.file.close()
        return content

    def save(self, commit=True):
        data = str(self.data['content']).lstrip()
        if not self.instance.file:
            tmp_file = NamedTemporaryFile(delete=True)
            self.instance.file.save(self.instance.generate_file_name(), tmp_file, save=False)
            tmp_file.close()

        with self.instance.file.open('w') as f:
            f.write(data)

        call_command('compilescss')
        return super(SiteStyleForm, self).save(commit)

    class Meta:
        model = SiteStyle
        fields = ['name', 'content', ]


@admin.register(SiteStyle)
class SiteStylesAdmin(SortableAdminMixin, admin.ModelAdmin):
    readonly_fields = ['file', ]
    form = SiteStyleForm
    list_display = ['name', 'filename', 'file_url']

    def filename(self, obj):
        return obj.file.name if obj.file else None
    filename.short_description = _('File name')

    def file_url(self, obj):
        return obj.file.url if obj.file else None
    file_url.short_description = _('File url')
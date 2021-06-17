import datetime
import json
import os
import zipfile
from io import StringIO, BytesIO
from json import JSONDecodeError

from adminsortable2.admin import SortableAdminMixin
from cms.admin.pageadmin import PageAdmin
from cms.models import Page, Placeholder, UserSettings
from django import forms
from django.contrib import admin, messages
from django.core.files.temp import NamedTemporaryFile
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from sass import CompileError
from sass_processor.processor import SassProcessor

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
        data = str(self.data['content']).strip()
        if not self.instance.file:
            tmp_file = NamedTemporaryFile(delete=True)
            self.instance.file.save(self.instance.generate_file_name(), tmp_file, save=True)
            tmp_file.close()

        with self.instance.file.open('w') as f:
            f.write(data)

        call_command('compilescss', stdout=StringIO())
        return super(SiteStyleForm, self).save(commit)

    class Meta:
        model = SiteStyle
        fields = ['name', 'content', 'site', ]


def export_styles(modeladmin, request, queryset):
    if queryset.count() == 1:
        file = queryset.first().file
        resp = HttpResponse(file.read(), content_type="text/scss")
        resp['Content-Disposition'] = 'attachment; filename=%s' % file.name

        return resp
    filenames = [s.file.path for s in queryset]
    zip_filename = "scss_export_%s.zip" % datetime.datetime.now().timestamp()

    zip_file = BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(zip_file, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(zip_file.getvalue(), content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


export_styles.short_description = _('Export selected')


class ImportView(TemplateView):
    template_name = 'cmsplus/admin/site_styles/import_styles.html'

    def get_context_data(self, **kwargs):
        r = super(ImportView, self).get_context_data(**kwargs)
        r.update({
            'title': _('Site Style'),
            'site_title': _('Import SCSS')
        })
        return r

    def post(self, request, *args, **kwargs):
        success = False
        errors = []

        for f in request.FILES.getlist('scss_files', []):
            f_name = str(f.name).split('.')[:-1]
            form = SiteStyleForm(data={
                'content': f.read().decode("utf-8"),
                'name': slugify(f_name),
            })

            if not form.is_valid():
                errors.append(form.errors)
            else:
                form.save(commit=True)

        if len(errors) < 1:
            success = True

        self.extra_context = self.extra_context if self.extra_context else {}
        self.extra_context.update({'success': success, 'errors': errors})

        if success:
            messages.success(request, _('Successfully imported styles'))
            url = reverse('admin:%s_%s_changelist' % (SiteStyle._meta.app_label,  SiteStyle._meta.model_name), )
            return HttpResponseRedirect(url)
        return self.get(request, *args, **kwargs)


@admin.register(SiteStyle)
class SiteStylesAdmin(SortableAdminMixin, admin.ModelAdmin):
    readonly_fields = ['file', ]
    form = SiteStyleForm
    list_display = ['name', 'filename', 'file_url', 'site']
    actions = [export_styles, ]
    change_list_template = 'cmsplus/admin/site_styles/change_list.html'

    def get_readonly_fields(self, request, obj=None):
        r = super().get_readonly_fields(request, obj)
        if obj:
            return ['name', ] + r
        return r

    def filename(self, obj):
        return obj.file.name if obj.file else None

    filename.short_description = _('File name')

    def file_url(self, obj):
        return obj.file.url if obj.file else None

    file_url.short_description = _('File url')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        try:
            sass_processor = SassProcessor()
            s = str(obj.path_for_template)
            sass_processor(s)
        except CompileError as e:
            self.message_user(request, e, level=messages.ERROR)

        return super().change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        return super(SiteStylesAdmin, self).get_urls() + [
            path('site_styles/import', ImportView.as_view(), name="site_styles_import"),
        ]

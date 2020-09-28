import json

from django import forms
from django.utils.translation import ugettext_lazy as _

from cmsplus.app_settings import cmsplus_settings
from cmsplus.forms import PlusPluginFormBase, get_style_form_fields, LinkFormBase
from cmsplus.models import PlusPlugin, LinkPluginMixin
from cmsplus.plugin_base import LinkPluginBase, StylePluginMixin


def get_visible_slides_fields():
    n_choices = [(n, '%d slides' % n) for n in range(1, 16)]
    fields = []
    for dev in reversed(cmsplus_settings.DEVICES):
        if dev == 'xl':
            initial = '3'
            required = True
            choices = n_choices
        else:
            initial = '1' if dev == 'sm' else ''
            required = False
            choices = [('', 'inherit'), ] + n_choices
        label = _('Num %s' % dev)

        field = forms.ChoiceField(label=label, required=required, choices=choices, initial=initial)
        fields.append(field)
    return fields


class SliderForm(PlusPluginFormBase):
    n_slides_xl, n_slides_lg, n_slides_md, n_slides_sm, n_slides_xs = get_visible_slides_fields()

    TYPE_CHOICES = (
        ('carousel', 'Carousel'),
        ('slider', 'Slider'),
    )
    type = forms.ChoiceField(
        label=_('Slider type'),
        initial='carousel',
        choices=TYPE_CHOICES,
        help_text=_('slider: rewinds slider to the start/end, carousel: circles.'),
    )

    gap = forms.IntegerField(
        label=_('Gap'),
        initial=10,
        help_text=_('Gap (px - default: 10) between slides.')
    )

    autoplay = forms.IntegerField(
        label=_('Autoplay'),
        initial=0,
        required=False,
        help_text=_('Duration (msec - default: 0) for infinite autoplay of slides (0 -> No autoplay.'),
    )

    animation_duration = forms.IntegerField(
        label=_('Animation Duration'),
        initial=400,
        required=False,
        help_text=_('Animation duration (msec - default: 400) - time between start and end of a slide change.'),
    )

    TIMING_FUNC_CHOICES = (
        ('cubic-bezier(0.165, 0.840, 0.440, 1.000)', 'Default'),
        ('linear', 'Linear'),
        ('ease', 'Ease'),
        ('ease-in', 'Ease In'),
        ('ease-out', 'Ease Out'),
        ('ease-in-out', 'Ease In/Out'),
        ('Bounce', 'Bounce'),
    )
    animation_timing_func = forms.ChoiceField(
        label=_('Animation Timing'),
        initial='cubic-bezier(0.165, 0.840, 0.440, 1.000)',
        choices=TIMING_FUNC_CHOICES,
        help_text=_('Animation timing, e.g.: Start: quick - end: slow.'),
    )

    hoverpause = forms.BooleanField(
        label=_('Hoverpause'),
        initial=True,
        required=False,
        help_text=_('Stop autoplay on mouse over.'),
    )

    peek = forms.IntegerField(
        label=_('Peek'),
        initial=0,
        help_text=_('Preview width (px) of next and previous hided slides.'),
    )

    STYLE_CHOICES = 'SLIDER_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class SliderPlugin(StylePluginMixin, LinkPluginBase):
    name = _("Slider")
    require_parent = False
    child_classes = ['SlidePlugin', ]
    allow_children = True
    alien_child_classes = False
    form = SliderForm
    render_template = 'cmsplus/generic/slider/slider.html'

    fieldsets = [
        (None, {
            'fields': (
                ('n_slides_xl', 'n_slides_lg', 'n_slides_md', 'n_slides_sm', 'n_slides_xs',),
                'type',
                'gap',
                'peek',
                ('autoplay', 'hoverpause',),
                ('animation_duration', 'animation_timing_func'),
            ),
            'description': _('Number of visible slides for the different device sizes:'),
        }),
        (_('Module settings'), {
            'classes': ('collapse',),
            'fields': (
                'extra_style', 'extra_classes', 'label',
            )
        }),
        (_('Extra CSS'), {
            'classes': ('collapse',),
            'fields': (
                'extra_css',
            )
        }),
    ]

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context['slider_config'] = json.dumps(instance.glossary)
        return context

    @classmethod
    def sanitize_model(cls, obj):
        breakpoints = {}
        for dev in reversed(cmsplus_settings.DEVICES):
            key = 'n_slides_%s' % dev
            width = cmsplus_settings.DEVICE_MAX_WIDTH_MAP[dev]
            if obj.glossary.get(key):
                breakpoints[width] = {'perView': int(obj.glossary[key])}
        obj.glossary['breakpoints'] = breakpoints
        return True


class SlideForm(LinkFormBase):
    require_link = False

    STYLE_CHOICES = 'SLIDE_STYLES'
    extra_style, extra_classes, label, extra_css = get_style_form_fields(STYLE_CHOICES)


class SlidePluginModel(PlusPlugin, LinkPluginMixin):
    class Meta:
        proxy = True


class SlidePlugin(StylePluginMixin, LinkPluginBase):
    name = _("Slide")
    parent_classes = ['SliderPlugin', ]
    allow_children = True
    alien_child_classes = True
    render_template = 'cmsplus/generic/slider/slider_child.html'
    model = SlidePluginModel

    form = SlideForm

    class Media:
        js = [
            'admin/js/jquery.init.js',
        ]

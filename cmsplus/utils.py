import copy
import datetime
import decimal
import json
import logging
import uuid
from typing import List

from io import StringIO
from html.parser import HTMLParser

from cms.api import create_page, create_title, add_plugin
from cms.models import Page, Placeholder
from django.core.exceptions import FieldError
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.functional import Promise

logger = logging.getLogger('cmsplus.utils')


def plus_add_plugin(placeholder, plugin_data, target=None):
    _add_plugin = {
        'placeholder': placeholder,
        'plugin_type': plugin_data.get('plugin_type'),
        'language': plugin_data.get('language'),
    }
    if plugin_data.get('is_plusplugin'):
        _add_plugin['data'] = plugin_data.get('data')
    else:
        _add_plugin = {**_add_plugin, **plugin_data.get('data')}

    generated_plugin = add_plugin(**_add_plugin, target=target)

    # add children recursively
    for plugin in plugin_data.get('children', []):
        plus_add_plugin(placeholder, plugin, target=generated_plugin)


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time/timedelta,
    decimal types, generators and other basic python objects.
    """

    def default(self, obj):
        # For Date Time string spec, see ECMA 262
        # https://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15
        if isinstance(obj, Promise):
            return force_str(obj)
        elif isinstance(obj, datetime.datetime):
            representation = obj.isoformat()
            if representation.endswith('+00:00'):
                representation = representation[:-6] + 'Z'
            return representation
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            if timezone and timezone.is_aware(obj):
                raise ValueError("JSON can't represent timezone-aware times.")
            representation = obj.isoformat()
            return representation
        elif isinstance(obj, datetime.timedelta):
            return str(obj.total_seconds())
        elif isinstance(obj, decimal.Decimal):
            # Serializers will coerce decimals to strings by default.
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, QuerySet):
            return tuple(obj)
        elif isinstance(obj, bytes):
            # Best-effort for binary blobs. See #4187.
            return obj.decode()
        elif hasattr(obj, 'tolist') and callable(obj.tolist):
            # Numpy arrays and array scalars.
            return obj.tolist()
        elif hasattr(obj, '__getitem__'):
            cls = (list if isinstance(obj, (list, tuple)) else dict)
            try:
                return cls(obj)
            except Exception:
                pass
        elif hasattr(obj, '__iter__'):
            return tuple(item for item in obj)
        return super().default(obj)


class PageUtils:
    _multi_lang_keys = ['title', 'menu_title', 'slug', 'published', 'redirect', 'meta_description', 'page_title', ]

    def __init__(self, page):
        self.page = page
        self.page_data = self.process_page(page)

    @staticmethod
    def process_page(page: Page) -> dict:
        _d_lang = {}

        # get values by language
        lang = page.get_languages()

        title = page.get_title()
        menu_title = page.get_menu_title()
        slug = page.get_slug()
        redirect = page.get_redirect()
        meta_description = page.get_meta_description()
        page_title = page.get_page_title()

        for i in range(1, len(lang)):
            c_lang = lang[i]
            _d_lang[c_lang] = {}
            _d_lang[c_lang]['title'] = page.get_title(c_lang)
            _d_lang[c_lang]['menu_title'] = page.get_menu_title(c_lang)
            _d_lang[c_lang]['slug'] = page.get_slug(c_lang)
            _d_lang[c_lang]['redirect'] = page.get_redirect(c_lang)
            _d_lang[c_lang]['meta_description'] = page.get_meta_description(c_lang)
            _d_lang[c_lang]['page_title'] = page.get_page_title(c_lang)

        page_data = {
            'title': title,
            'template': page.get_template(),
            'languages': page.get_languages(),
            'menu_title': menu_title,
            'slug': slug,
            'created_by': 'shop',
            'position': 'first-child',

            'apphook': page.application_urls,
            'apphook_namespace': page.application_namespace,
            'redirect': redirect,
            'meta_description': meta_description,
            'in_navigation': page.in_navigation,
            'soft_root': page.soft_root,
            'reverse_id': page.reverse_id,
            'published': False,
            'login_required': page.login_required,
            'page_title': page_title,
            'navigation_extenders': page.navigation_extenders,
            'is_home': page.is_home,

            'additional_languages': _d_lang,
            'children': [],
            'plugins': {},
        }

        placeholder: Placeholder
        for placeholder in page.get_placeholders():
            if placeholder.get_plugins().count() < 1:
                continue

            plugin_tree = generate_plugin_tree(placeholder)
            page_data['plugins'][placeholder.slot] = plugin_tree  # noqa

        child: Page
        for child in page.get_child_pages():
            # noinspection PyTypeChecker
            page_data['children'].append(PageUtils.process_page(child))

        return page_data

    @staticmethod
    def export_whole_site():
        pages_data = []
        for p in Page.objects.filter(publisher_is_draft=True, node__parent=None):
            pu = PageUtils(p)
            pages_data.append(pu.page_data)
        return pages_data

    @staticmethod
    def import_pages(pages_data: list):
        generate_structure(pages_data)

    @staticmethod
    def count_pages(page_data, count=0):
        for p in page_data:
            count += 1
            if p.get('children'):
                count = PageUtils.count_pages(p['children'], count)
        return count

    @staticmethod
    def _count_plugins_helper(plugin_list: list, count=0) -> int:
        for p in plugin_list:
            count += 1
            logger.debug(f'Importing plugin "{p.get("plugin_type")}"')
            if p.get('children'):
                count = PageUtils._count_plugins_helper(p['children'], count)
        return count

    @staticmethod
    def count_plugins(plugins_data: list, count=0) -> int:
        for plugin in plugins_data:
            placeholders = plugin.get('plugins')
            for placeholder, plugins in placeholders.items():
                logger.debug(f'-> Page "{plugin.get("title")}"')
                count = PageUtils._count_plugins_helper(plugins, count)

            if plugin.get('children'):
                PageUtils.count_plugins(plugin['children'], count)
        return count


def generate_plugin_tree(placeholder, language=None):
    if language:
        plugins = placeholder.get_plugins().filter(language=language)
    else:
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

        from cmsplus.plugin_base import PlusPluginBase
        if issubclass(p.__class__, PlusPluginBase):
            plugin_data['data'] = instance._json
            plugin_data['is_plusplugin'] = True

        # handle django cms plugins
        else:
            plugin_fields = p.form.base_fields
            data = {}
            for field in plugin_fields:
                if hasattr(instance, field):
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

    return plugin_tree


def generate_structure(structure: List[dict], parent: object = None, force: object = False, skip_plugins=None):
    _structure = copy.deepcopy(structure)
    if not parent:
        logger.debug('\n--- Root Level ---')
    else:
        logger.debug(f'\n--- Parent: {parent} ---')
    logger.debug(f'Found {len(structure)} pages')

    for page in _structure:
        languages = page.pop('languages')
        plugins = page.pop('plugins')
        is_home = page.pop('is_home', False)

        additional_languages = page.pop('additional_languages')
        title = page.get('title')

        logger.info(f'Processing Page "{title}"')

        children = page.pop('children')
        logger.debug(f'Page has {len(children)} sub pages')

        if parent:
            page['parent'] = parent

        rid = page.get('reverse_id')
        if force and rid:
            logger.info(f'Forced creating Page with {rid}')
            Page.objects.filter(reverse_id=rid).delete()

        try:
            p = create_page(
                language=languages[0],
                **page
            )
        except FieldError as e:
            logger.error(e)
            continue

        # set home
        if is_home:
            p.is_home = True

        # create additional titles (multi lang)
        for lang, value in additional_languages.items():
            create_title(
                language=lang,
                page=p,
                **value,
            )

        # generate plugins for page
        if not skip_plugins:
            for placeholder_slot, data in plugins.items():
                try:
                    placeholder = p.placeholders.get(slot=placeholder_slot)
                except Placeholder.DoesNotExist:
                    logger.error(f'Placeholder slot "{placeholder_slot}" does not exist')
                    continue

                for plugin_data in data:
                    plus_add_plugin(
                        placeholder=placeholder,
                        plugin_data=plugin_data
                    )

        # create plugins
        if children:
            generate_structure(children, parent=p, force=force)


class HtmlTagStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_html_tags(html):
    s = HtmlTagStripper()
    s.feed(html)
    return s.get_data()

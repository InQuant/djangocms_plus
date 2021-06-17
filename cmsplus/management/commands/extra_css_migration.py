import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand

from cmsplus.app_settings import cmsplus_settings as cps
from cmsplus.models import PlusPlugin

logging.basicConfig(level=logging.INFO, format='%(message)s')

logger = logging.getLogger()


class Command(BaseCommand):
    help = 'Migrate old "extra css" dicts'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-d', '--dry-run', help='Show files without deleting', action='store_true')

    @staticmethod
    def render(instance):
        _css = Command.get_extra_css(instance)
        r = []
        for media, css_attrs in _css.items():
            _css_attrs = []
            for attr in css_attrs:
                _css_attrs.append(f'{attr[0]}: {attr[1]};')

            css = '\n'.join(_css_attrs)

            _css_line = f'.c-extra-{instance.id} {{\n{css}\n}}'
            if media != 'default':
                _css_line = f'{media} {{\n{_css_line}\n}}'
            r.append(_css_line)

        return '\n'.join(r)

    @staticmethod
    def get_extra_css(instance):
        """
        gets the extra (device specific) css styles

        extra_css is stored device specific in glossary like this:
        extra_css : {
            'margin-bottom': '7rem',
            'margin-bottom:md': '13rem',
            'margin-bottom:xl': '30rem',
            'color': 'red',
            'color:md': 'blue',
        }

        returns from example:
            [
                'default', [
                    ('margin-bottom', '7rem'),
                    ('color', 'red'),
                ],
                '@media (min-width: 768px)', [
                    ('margin-bottom', '13rem'),
                    ('color', 'blue'),
                ],
                '@media (min-width: 768px)', [
                    ('margin-bottom', '30rem'),
                ],
            ]
        """

        def _get_media_and_css_key(key):
            """
            from e.g: margin-bottom:md ->  returns '@media (min-width: 768px)', margin-bottom
            """
            try:
                # k e.g. md:margin-bottom
                css_key, dev = key.split(':')
                media = '@media (min-width: %spx)' % cps.DEVICE_MIN_WIDTH_MAP.get(dev, 'xs')
            except ValueError:
                css_key = key
                media = 'default'
            return media, css_key

        css = {}

        for key, val in instance.glossary.get('extra_css', {}).items():
            media, css_key = _get_media_and_css_key(key)
            if media in css:
                _list = css[media]
                _list.append((css_key, val))
                css[media] = _list
            else:
                css[media] = [(css_key, val), ]
        return css

    def migrate_plugins(self, dry_run=False):
        count = 0
        for plugin in PlusPlugin.objects.all():
            pi, pc = plugin.get_plugin_instance()
            extra_css = pi.glossary.get('extra_css')
            if not extra_css or not isinstance(extra_css, dict):
                continue

            self.stdout.write('Found plugin "%s (ID: %s)" (%s)' % (plugin, pi.id, str(extra_css)[:100]+'...'))
            if dry_run:
                continue

            plugin._json['extra_css'] = self.render(pi)
            plugin.save()
            count += 1
        if not dry_run:
            self.stdout.write('\nMigrated %i plugins' % count)

    def handle(self, *args, **options):
        dry_run = options.get('dry_run') or False

        if options.get('verbosity') and options['verbosity'] > 1:
            logger.setLevel(logging.DEBUG)
            logger.debug('\n[Setting logger to DEBUG]')

        if dry_run:
            logger.info(f'--- dry run ---')#

        self.migrate_plugins(dry_run)


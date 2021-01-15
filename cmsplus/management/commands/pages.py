import json
import logging
import sys
from json import JSONDecodeError

from django.core.management import BaseCommand, CommandError

from cmsplus.utils import PageUtils

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Import or Export page structures'

    def add_arguments(self, parser):
        parser.add_argument('command', type=str, choices=['import', 'export'])
        parser.add_argument("-o", "--output", help="Output JSON file path")
        parser.add_argument("-i", "--input", help="Input JSON file path")
        parser.add_argument("-p", "--page", type=int, help="Export: Start from given page id")

    def handle(self, *args, **options):
        if options.get('verbosity') and options['verbosity'] > 1:
            logger.info('\n[Setting logger to DEBUG]')
            logger.setLevel(logging.DEBUG)

        if options.get('command'):
            if options['command'] == 'import':
                data = None
                data_stdin = None
                if not sys.stdin.isatty():
                    data_stdin = sys.stdin.read()

                self.stdout.write('\n-- Importing pages --')

                if not options.get('input') and not data_stdin:
                    raise CommandError('No input provides. Either use -i (or --input) or through piping')

                if options.get('input'):
                    f_path = options.get('input')
                    try:
                        with open(f_path, 'r') as file:
                            data = json.loads(file.read())
                    except JSONDecodeError as e:
                        self.stdout.write(self.style.ERROR(f'JSON File "{f_path}" invalid.\n{e}'))
                    except FileNotFoundError as e:
                        self.stdout.write(self.style.ERROR(f'File not found: {f_path}'))

                elif data_stdin:
                    try:
                        data = json.loads(data_stdin)
                    except JSONDecodeError as e:
                        self.stdout.write(self.style.ERROR(f'JSON Input invalid.\n{e}'))

                PageUtils.import_pages(data)
                page_count = PageUtils.count_pages(data)
                plugins_count = PageUtils.count_plugins(data)
                self.stdout.write(self.style.SUCCESS('Imported:'))
                self.stdout.write(self.style.SUCCESS(f'-> Pages: {page_count} '))
                self.stdout.write(self.style.SUCCESS(f'-> Plugins: {plugins_count} '))

            elif options['command'] == 'export':
                self.stdout.write('\n-- Exporting pages --')
                if options.get('page'):
                    from cms.models import Page
                    try:
                        p = Page.objects.get(id=options['page'])
                    except Page.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'Page with id "{options["page"]}" does not exist'))
                        return
                    else:
                        data = [PageUtils(page=p).page_data]
                else:
                    data = PageUtils.export_whole_site()

                if not options.get('output'):
                    self.stdout.write(data)
                    return

                f_path = options.get('output')
                json_data = json.dumps(data, indent=True, ensure_ascii=False)
                with open(f_path, 'w') as file:
                    file.write(json_data)

                self.stdout.write(self.style.SUCCESS(f'Exported to "{f_path}":'))
                page_count = PageUtils.count_pages(data)
                plugins_count = PageUtils.count_plugins(data)
                self.stdout.write(self.style.SUCCESS(f'-> Pages: {page_count} '))
                self.stdout.write(self.style.SUCCESS(f'-> Plugins: {plugins_count} '))


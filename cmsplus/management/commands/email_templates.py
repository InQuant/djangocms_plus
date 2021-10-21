import json
import logging
import sys

from django.core.management import BaseCommand, CommandError
from post_office.models import EmailTemplate

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Import or Export email templates'

    def add_arguments(self, parser):
        parser.add_argument('command', type=str, choices=['import', 'export'])
        parser.add_argument("-f", "--file", help="Output JSON file path")
        parser.add_argument("-u", "--update", type=bool, const=True, default=False, nargs='?', help="Update templates if existing")

    def handle(self, *args, **options):
        if options.get('verbosity') and options['verbosity'] > 1:
            logger.info('\n[Setting logger to DEBUG]')
            logger.setLevel(logging.DEBUG)

        if options['command'] == 'export':
            self.stdout.write('--- Exporting EmailTemplates ---')
            output = self.export_templates()
            output = json.dumps(output, ensure_ascii=False, indent=False)

            if options.get('file'):
                f_path = options.get('file')
                with open(f_path, 'w') as f:
                    f.write(output)
                self.stdout.write(self.style.SUCCESS(f'Export output written to "{f_path}"'))
            else:
                self.stdout.write(output)

        elif options['command'] == 'import':
            self.stdout.write('--- Importing EmailTemplates ---')
            if options.get('file'):
                f_path = options.get('file')
                with open(f_path, 'r') as f:
                    data = json.loads(f.read())

            elif not sys.stdin.isatty():
                data = json.loads(sys.stdin.read())

            else:
                raise CommandError('No input defined')

            self.import_templates(data, update=options.get('update'))

    def export_templates(self):
        data = []
        t_count = 0
        t_count_default = 0
        fields = [f.name for f in EmailTemplate._meta.fields]
        for t in EmailTemplate.objects.all():
            template_data = {}
            for f in fields:

                if f in ['last_updated', 'created']:
                    continue

                value = getattr(t, f, None)
                if f == 'default_template':
                    if not value:
                        t_count_default += 1

                    if issubclass(EmailTemplate, value.__class__):
                        value = value.name

                template_data[f] = value

            data.append(template_data)
            t_count += 1

        self.stdout.write(self.style.SUCCESS(f'EmailTemplates exported: {t_count}'))
        self.stdout.write(self.style.SUCCESS(f'Default EmailTemplates: {t_count_default}'))
        return data

    def import_templates(self, data, update=False):
        t_count_created = 0
        t_count_updated = 0
        t_count_skipped = 0

        for template_data in data:
            logger.debug(f'Processing "{template_data.get("name")}" (update is {bool(update)})')
            name = template_data.get('name')
            lang = template_data.get('language')

            qs = EmailTemplate.objects.filter(name=name, language=lang)

            if qs.count() > 0:
                logger.debug('Template already in DB')
                if not update:
                    t_count_skipped += 1
                    continue

            if template_data.get('default_template'):
                name = template_data.get('default_template')
                try:
                    template_data['default_template'] = EmailTemplate.objects.get(name=name, language='')
                except EmailTemplate.DoesNotExist:
                    logger.error(f'Default EmailTemplate with name "{name}" not found')
                    template_data['default_template'] = None

            obj, created = EmailTemplate.objects.update_or_create(**template_data)
            if created:
                action = 'Created'
                t_count_created += 1
            else:
                action = 'Updated'
                t_count_updated += 1

            logger.debug(f'{action} "{obj.name}" {str(obj.language).upper()}')
        self.stdout.write(self.style.SUCCESS('EmailTemplates'))
        self.stdout.write(self.style.SUCCESS(f'-> created: {t_count_created}'))
        self.stdout.write(self.style.SUCCESS(f'-> updated: {t_count_updated}'))
        self.stdout.write(self.style.SUCCESS(f'-> skipped: {t_count_skipped}'))

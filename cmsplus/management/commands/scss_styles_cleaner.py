import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand

from cmsplus.models import SiteStyle, scss_storage

logging.basicConfig(level=logging.INFO, format='%(message)s')

logger = logging.getLogger()


class Command(BaseCommand):
    help = 'Clean up unused Site Styles scss files'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-d', '--dry-run', help='Show files without deleting', action='store_true')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run') or False
        if options.get('verbosity') and options['verbosity'] > 1:
            logger.setLevel(logging.DEBUG)
            logger.debug('\n[Setting logger to DEBUG]')

        if dry_run:
            logger.info(f'--- dry run ---')

        existing_files = scss_storage.listdir('')[1]
        obj_files = SiteStyle.objects.values_list('file', flat=True)

        logger.debug('Existing files in directory: \n%s\n' % '\n'.join(existing_files))
        logger.debug('Files in objects: \n%s\n' % ("\n".join(obj_files),))

        to_delete = [f for f in existing_files if f not in obj_files]

        self.stdout.write("Will delete files: \n%s\n" % ("\n".join(to_delete),))

        if dry_run:
            return

        sure_input = input(f'\nDelete {len(to_delete)} files. Sure? (y/N)')
        if not sure_input == 'y':
            self.stdout.write('Canceled')
            return

        count = 0
        for f in to_delete:
            try:
                scss_storage.delete(f)
            except Exception as e:
                logger.exception(e)
                continue
            count += 1

        self.stdout.write(f'Deleted {count} files.')

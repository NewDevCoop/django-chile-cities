from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load Chile cities into database"

    def handle(self, *args, **options):
        with transaction.atomic():
            call_command('loaddata', 'region')
            call_command('loaddata', 'province')
            call_command('loaddata', 'city')

            self.stdout.write(
                self.style.SUCCESS('Script executed Succesfully.')
            )

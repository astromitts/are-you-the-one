from django.core.management.base import BaseCommand, CommandError
from ayto.utils import pre_populate_db


class Command(BaseCommand):
    help = 'Pre-populates Participant instances'


    def handle(self, *args, **options):
        pre_populate_db()

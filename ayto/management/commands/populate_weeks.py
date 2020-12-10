from django.core.management.base import BaseCommand, CommandError
from ayto.models import Week


class Command(BaseCommand):
    help = 'Pre-populates week instances'

    def add_arguments(self, parser):
        parser.add_argument('num_weeks', type=int)

    def handle(self, *args, **options):
        for i in range(1, options['num_weeks'] + 1):
            Week.objects.filter(week_number=i).all().delete()
            week = Week(week_number=i)
            week.save()

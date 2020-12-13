from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
import json

from ayto.models import Week
from ayto.utils import load_week_from_json


class Command(BaseCommand):
    help = 'Dump matchup data from given week'


    def add_arguments(self, parser):
        parser.add_argument('week_number', type=int)


    def handle(self, *args, **options):
        week_number = options['week_number']
        try:
            with open('data/week{}.json'.format(week_number)) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError('Data for week {} not found'.format(week_number))
        try:
            week = Week.objects.get(week_number=week_number)
        except Week.DoesNotExist:
            error = 'Week {} not found. Perhaps you need to run `manage.py populate` first?'.format(week_number)
            raise CommandError(error)

        load_week_from_json(week, data)

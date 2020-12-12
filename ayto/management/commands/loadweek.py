from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
import json

from ayto.models import (
    Week,
    Matchup,
    PotentialMatchup,
    TruthBooth
)


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
        week.matches_count = data['matches_count']
        week.locked = data['locked']
        week.save()

        for match in data['matchups']:
            source_matchup = PotentialMatchup.get(match['participant1'], match['participant2'])
            matchup = Matchup(
                week=week,
                matchup=source_matchup
            )
            try:
                matchup.save()
            except IntegrityError:
                pass

        for match in data['truthbooths']:
            source_matchup = PotentialMatchup.get(match['participant1'], match['participant2'])
            matchup = TruthBooth(
                week=week,
                matchup=source_matchup,
                perfect_match=match['perfect_match']
            )
            try:
                matchup.save()
            except IntegrityError:
                matchup.update(perfect_match=perfect_match)

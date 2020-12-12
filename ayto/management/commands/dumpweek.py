from django.core.management.base import BaseCommand, CommandError
import json

from ayto.models import Week


class Command(BaseCommand):
    help = 'Dump matchup data from given week'


    def add_arguments(self, parser):
        parser.add_argument('week_number', type=int)


    def handle(self, *args, **options):
        week = Week.objects.get(week_number=options['week_number'])
        data = {
            'week': week.week_number,
            'locked': week.locked,
            'matches_count': week.matches_count,
            'matchups': [],
            'truthbooths': []
        }

        for match in week.matchup_set.all():
            data['matchups'].append({
                'participant1': match.matchup.participant1.full_name,
                'participant2': match.matchup.participant2.full_name
            })

        for match in week.truthbooth_set.all():
            data['truthbooths'].append({
                'participant1': match.matchup.participant1.full_name,
                'participant2': match.matchup.participant2.full_name,
                'perfect_match': match.perfect_match
            })

        with open('data/week{}.json'.format(week.week_number), 'w+') as f:
            f.write(json.dumps(data))
        print(json.dumps(data))

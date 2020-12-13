from ayto.models import (
    Participant,
    PotentialMatchup,
    Matchup,
    TruthBooth,
    Week,
)
from ayto.participant_data import PARTICIPANTS
from django.db.utils import IntegrityError

import json


def load_filedata_for_week(week_number):
    week = Week.objects.get(week_number=week_number)
    with open('data/week{}.json'.format(week_number)) as f:
        data = json.load(f)
    load_week_from_json(week, data)


def load_week_from_json(week, json_data):
    week.matches_count = json_data['matches_count']
    week.locked = json_data['locked']
    week.save()

    for match in json_data['matchups']:
        source_matchup = PotentialMatchup.get(match['participant1'], match['participant2'])
        matchup = Matchup(
            week=week,
            matchup=source_matchup
        )
        try:
            matchup.save()
        except IntegrityError:
            pass

    for match in json_data['truthbooths']:
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


def pre_populate_db():
    Week.objects.all().delete()
    Participant.objects.all().delete()
    PotentialMatchup.objects.all().delete()

    for i in range(1, 11):
        week = Week(week_number=i)
        week.save()

    for participant in PARTICIPANTS:
        if not participant.get('name'):
            participant['name'] = participant['full_name'].split(' ')[0]
        participant['url_slug'] = participant['full_name'].lower().replace(' ', '-')
        participant_obj = Participant(**participant)
        participant_obj.save()

    all_participants = Participant.objects.all()
    potential_matchups = []
    for participant in all_participants:
        other_participants = Participant.objects.exclude(pk=participant.pk).all()
        for op in other_participants:
            form1 = [participant, op]
            form2 = [op, participant]
            if form1 not in potential_matchups and form2 not in potential_matchups:
                potential_matchup = PotentialMatchup(
                    participant1=participant,
                    participant2=op
                )
                potential_matchup.save()
                potential_matchups.append([participant, op])

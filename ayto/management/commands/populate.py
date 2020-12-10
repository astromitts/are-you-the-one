from django.core.management.base import BaseCommand, CommandError
from ayto.models import Participant, PotentialMatchup, Week


PARTICIPANTS = [
    {
        'full_name': 'Aasha Wells',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-18-2000.jpg',
    },
    {
        'full_name': 'Amber Martinez',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-17-2000.jpg',
    },

    {
        'full_name': 'Basit Shittu',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-15-2000.jpg',
    },
    {
        'full_name': 'Brandon Davis',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-14-2000.jpg',
    },
    {
        'full_name': 'Danny Prikazsky',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-13-2000.jpg',
    },
    {
        'full_name': 'Jasmine Olson',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-11-2000.jpg',
    },
    {
        'full_name': 'Jenna Brown',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-10-2000.jpg',
    },
    {
        'full_name': 'Jonathan Short',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-9-2000.jpg',
    },
    {
        'name': 'Justin',
        'full_name': 'Justinavery Palm',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-8-2000.jpg',
    },
    {
        'full_name': 'Kai Wes',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-7-2000.jpg',
    },
    {
        'full_name': 'Kari Snow',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-6-2000.jpg',
    },
    {
        'full_name': 'Kylie Smith',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-5-2000.jpg',
    },
    {
        'full_name': 'Max Gentile',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-4-2000.jpg',
    },
    {
        'full_name': 'Nour Fraij',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-3-2000.jpg',
    },
    {
        'full_name': 'Paige Cole',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-2-2000.jpg',
    },
    {
        'full_name': 'Remy Duran',
        'picture': 'https://static.onecms.io/wp-content/uploads/sites/6/2019/05/are-you-the-one-1-2000.jpg',
    },
]

class Command(BaseCommand):
    help = 'Pre-populates Participant instances'


    def handle(self, *args, **options):
        Week.objects.all().delete()
        Participant.objects.all().delete()
        PotentialMatchup.objects.all().delete()

        for i in range(1, 9):
            week = Week(week_number=i)
            week.save()

        for participant in PARTICIPANTS:
            if not participant.get('name'):
                participant['name'] = participant['full_name'].split(' ')[0]
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


from django.test import TestCase

from ayto.models import (
    Matchup,
    Participant,
    PotentialMatchup,
    TruthBooth,
    Week,
)
from ayto.utils import pre_populate_db, load_filedata_for_week


class AytoDataTest(TestCase):
    def setUp(self):
        super(AytoDataTest, self).setUp()
        pre_populate_db()
        load_filedata_for_week(1)
        load_filedata_for_week(2)
        load_filedata_for_week(3)

        self.test_week = Week.objects.get(week_number=4)


class TestMatchLogic(AytoDataTest):
    def test_truthbooth_match_eliminates_related_matches(self):
        """ Verify if Max and Paige are a Truth Booth perfect match, all of their
            other potential matches are marked eliminated via truthbooth and
            they are marked as perfect match via truthbooth
        """
        _max = Participant.objects.get(name='Max')
        _paige = Participant.objects.get(name='Paige')
        max_paige_matchup = PotentialMatchup.get(_max, _paige)
        week4_truthbooth = TruthBooth(
            week=self.test_week,
            matchup=max_paige_matchup,
            perfect_match=True
        )
        week4_truthbooth.save()

        max_matchups = _max.potential_matchups
        paige_found = False
        others_found = False
        for matchup in max_matchups:
            if matchup['match'] != _paige:
                others_found = True
                self.assertTrue(matchup['eliminated'])
                self.assertEqual(
                    matchup['elimination_type'],
                    'Eliminated Via Truthbooth'
                )
            else:
                paige_found = True
                self.assertFalse(matchup['eliminated'])
                self.assertEqual(
                    matchup['elimination_type'],
                    'Perfect Match: Truth Booth'
                )
        self.assertTrue(paige_found)
        self.assertTrue(others_found)


    def test_blackout_elimination_logic(self):
        """ Verify that when a week has 0 matches, all participating matchups
            get marked as eliminated
        """
        black_out_matches = [
            ('Brandon', 'Kylie'),
            ('Aasha', 'Max'),
            ('Amber', 'Paige'),
            ('Danny', 'Remy'),
            ('Jasmine', 'Justin'),
            ('Jenna', 'Kai'),
            ('Nour', 'Kari'),
            ('Jonathan', 'Basit'),
        ]

        for black_out_match in black_out_matches:
            potential_matchup = PotentialMatchup.get(
                black_out_match[0], black_out_match[1])
            match = Matchup(
                week=self.test_week,
                matchup=potential_matchup
            )
            match.save()
        self.test_week.matches_count = 0
        self.test_week.locked = True
        self.test_week.save()

        for black_out_match in black_out_matches:
            potential_matchup = PotentialMatchup.get(
                black_out_match[0], black_out_match[1])
            self.assertTrue(potential_matchup.eliminated_via_blackout)

        self.test_week.matches_count = 1
        self.test_week.locked = True
        self.test_week.save()

        for black_out_match in black_out_matches:
            potential_matchup = PotentialMatchup.get(
                black_out_match[0], black_out_match[1])
            self.assertFalse(potential_matchup.eliminated_via_blackout)


    def test_all_matches_logic(self):
        perfect_matches = [
            ('Brandon', 'Kylie'),
            ('Aasha', 'Max'),
            ('Amber', 'Paige'),
            ('Danny', 'Remy'),
            ('Jasmine', 'Justin'),
            ('Jenna', 'Kai'),
            ('Nour', 'Kari'),
            ('Jonathan', 'Basit'),
        ]

        for perfect_match in perfect_matches:
            potential_matchup = PotentialMatchup.get(
                perfect_match[0], perfect_match[1])
            match = Matchup(
                week=self.test_week,
                matchup=potential_matchup
            )
            match.save()

        self.test_week.matches_count = 8
        self.test_week.locked = True
        self.test_week.save()

        for perfect_match in perfect_matches:
            potential_matchup = PotentialMatchup.get(
                perfect_match[0], perfect_match[1])
            self.assertTrue(potential_matchup.perfect_match)

        self.test_week.matches_count = 3
        self.test_week.locked = True
        self.test_week.save()

        for perfect_match in perfect_matches:
            potential_matchup = PotentialMatchup.get(
                perfect_match[0], perfect_match[1])
            self.assertFalse(potential_matchup.perfect_match)

    def test_truthbooth_related_eliminations(self):
        truthbooth_participant1 = 'Justin'
        truthbooth_participant2 = 'Kai'

        test_matchup = PotentialMatchup.get(
            truthbooth_participant1, truthbooth_participant2)

        TruthBooth.lock(
            week=self.test_week,
            participant1=truthbooth_participant1,
            participant2=truthbooth_participant2,
            perfect_match=True
        )

        self.assertFalse(test_matchup.perfect_match_via_truthbooth)

        other_matchup_verified = False  # guard against false positive
        for matchup in test_matchup.related_matchups:
            if matchup != test_matchup:
                self.assertTrue(matchup.eliminated_via_truthbooth)
                other_matchup_verified = True
        self.assertTrue(other_matchup_verified)

        truthbooth = TruthBooth.lock(
            week=self.test_week,
            participant1=truthbooth_participant1,
            participant2=truthbooth_participant2,
            perfect_match=False
        )

        self.assertFalse(test_matchup.perfect_match_via_truthbooth)

        other_matchup_verified = False  # guard against false positive
        for matchup in test_matchup.related_matchups:
            if matchup != test_matchup:
                self.assertFalse(matchup.eliminated_via_truthbooth)
                other_matchup_verified = True
        self.assertTrue(other_matchup_verified)

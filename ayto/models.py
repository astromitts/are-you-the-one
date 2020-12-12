from django.db import models


class Participant(models.Model):
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    picture = models.URLField(blank=True, null=True)
    url_slug = models.CharField(max_length=100, unique=True)

    @property
    def perfect_match(self):
        return self.potentialmatchup_qs.filter(perfect_match=True).first()

    @property
    def potentialmatchup_qs(self):
        return PotentialMatchup.objects.order_by('pk').filter(
            models.Q(participant1=self) |
            models.Q(participant2=self)
        )

    @property
    def potential_matchups(self):
        matchups = self.potentialmatchup_qs.all()
        formatted_matchups = []
        for matchup in matchups:
            formatted_matchup = {
                'eliminated': matchup.eliminated,
                'elimination_type': matchup.elimination_type,
                'potentialmatchup': matchup,
                'weeks_matched': matchup.matchup_set.all()
            }
            if matchup.participant1 == self:
                formatted_matchup['match'] = matchup.participant2
            else:
                formatted_matchup['match'] = matchup.participant1
            formatted_matchups.append(formatted_matchup)
        return formatted_matchups

    @property
    def eliminated_matchups(self):
        matchups = PotentialMatchup.objects.filter(
            models.Q(participant1=self) |
            models.Q(participant2=self)
        ).filter(
            models.Q(eliminated_via_blackout=True) |
            models.Q(eliminated_via_truthbooth=True) |
            models.Q(manually_eliminated=True)
        ).all()
        formatted_matchups = []
        for matchup in matchups:
            if matchup.participant1 == self:
                formatted_matchups.append(
                    {
                        'match': matchup.participant2,
                        'elimination_type': matchup.elimination_type
                    }
                )
            else:
                formatted_matchups.append(
                    {
                        'match': matchup.participant1,
                        'elimination_type': matchup.elimination_type
                    }
                )
        return formatted_matchups


    def __str__(self):
        return self.full_name


class Week(models.Model):
    week_number = models.IntegerField()
    matches_count = models.IntegerField(default=0)
    locked = models.BooleanField(default=False)

    def __str__(self):
        return 'Week #{}'.format(self.week_number)

    @classmethod
    def get_set_weeks(cls):
        weeks = []
        for week in cls.objects.all().order_by('-week_number'):
            if week.matchup_set.count() > 0 or week.truthbooth_set.count() > 0:
                weeks.append(week)
        return weeks

    def get_available_participants(self):
        unavailable_participants = []
        # for tb in self.truthbooth_set.all():
        #     unavailable_participants.append(tb.matchup.participant1)
        #     unavailable_participants.append(tb.matchup.participant2)

        for pm in PotentialMatchup.objects.filter(perfect_match=True):
            unavailable_participants.append(pm.participant1)
            unavailable_participants.append(pm.participant2)

        for mu in self.matchup_set.all():
            unavailable_participants.append(mu.matchup.participant1)
            unavailable_participants.append(mu.matchup.participant2)


        available_participants = Participant.objects.exclude(
            pk__in=[p.pk for p in unavailable_participants]
        )
        return available_participants

    def save(self, *args, **kwargs):
        super(Week, self).save(*args, **kwargs)
        if self.matches_count == 0:
            for matchup in self.matchup_set.all():
                matchup.matchup.eliminated_via_blackout = True
                matchup.matchup.save()

    def get_overlaps(self):
        overlaps = {}
        this_week_matchups = [ms.matchup for ms in self.matchup_set.all()]
        for week in Week.objects.exclude(pk=self.pk).all():
            diff_week_matchups = [ms.matchup for ms in week.matchup_set.all()]
            diff_overlaps = []
            for matchup in diff_week_matchups:
                if matchup in this_week_matchups:
                    diff_overlaps.append(matchup)
            if diff_overlaps:
                overlaps[week] = diff_overlaps
        return overlaps


    def get_overlaps_for_participant(self, participant):
        this_week_overlaps = self.get_overlaps
        overlaps_for_participant = {}
        for week, overlaps in this_week_overlaps.items():
            participant_in_matches = False
            for overlap in overlaps:
                if participant in [overlap.participant1, overlap.participant2]:
                    participant_in_matches = True
            if participant_in_matches:
                overlaps_for_participant[week] = overlaps


class PotentialMatchup(models.Model):
    participant1 = models.ForeignKey(
        Participant,
        related_name='potential_matchup_participant1',
        on_delete=models.CASCADE
    )
    participant2 = models.ForeignKey(
        Participant,
        related_name='potential_matchup_participant2',
        on_delete=models.CASCADE
    )
    speculative_match = models.BooleanField(default=False)
    perfect_match = models.BooleanField(default=False)
    perfect_match_via_truthbooth = models.BooleanField(default=False)
    manually_eliminated = models.BooleanField(default=False)
    eliminated_via_truthbooth = models.BooleanField(default=False)
    eliminated_via_blackout = models.BooleanField(default=False)

    class Meta:
        unique_together = ['participant1', 'participant2']

    @property
    def eliminated(self):
        if self.eliminated_via_truthbooth or self.eliminated_via_blackout:
            return True
        else:
            return self.manually_eliminated

    @property
    def elimination_type(self):
        if self.eliminated_via_truthbooth:
            return 'Eliminated Via Truthbooth'
        elif self.eliminated_via_blackout:
            return 'Eliminated Via Blackout'
        elif self.manually_eliminated:
            return 'Manual Elimination'
        elif self.perfect_match:
            if self.perfect_match_via_truthbooth:
                return 'Perfect Match: Truth Booth'
            return 'Final Match'
        elif self.speculative_match:
            return 'Speculative Match'
        return "can't be eliminated"

    @property
    def elimination_tag(self):
        if self.eliminated_via_truthbooth:
            return 'eliminated_via_truthbooth'
        elif self.eliminated_via_blackout:
            return 'eliminated_via_blackout'
        elif self.manually_eliminated:
            return 'manual_elimination'
        elif self.perfect_match:
            return 'perfect_match'
        elif self.speculative_match:
            return 'speculative_match'
        return 'not_eliminated'

    @classmethod
    def get(cls, participant1, participant2):
        if isinstance(participant1, str):
            participant1 = Participant.objects.get(full_name=participant1)

        if isinstance(participant2, str):
            participant2 = Participant.objects.get(full_name=participant2)

        return cls.objects.filter(
            models.Q(participant1=participant1) |
            models.Q(participant2=participant1)
        ).filter(
            models.Q(participant1=participant2) |
            models.Q(participant2=participant2)
        ).first()

    def set_perfect_match(self, match_type):
        related_matchups = PotentialMatchup.objects.filter(
            models.Q(participant1__in=[self.participant1, self.participant2]) |
            models.Q(participant2__in=[self.participant1, self.participant2])
        ).exclude(pk=self.pk).all()
        for matchup in related_matchups:
            if match_type == 'truthbooth':
                matchup.eliminated_via_truthbooth = True
            else:
                matchup.manually_eliminated = True
            matchup.save()
        self.perfect_match = True
        self.save()


    def unset_perfect_match(self):
        related_matchups = PotentialMatchup.objects.filter(
            models.Q(participant1__in=[self.participant1, self.participant2]) |
            models.Q(participant2__in=[self.participant1, self.participant2])
        ).exclude(pk=self.pk).all()
        for matchup in related_matchups:
            matchup.eliminated_via_truthbooth = False
            matchup.manually_eliminated = False
            matchup.save()
        self.perfect_match = False
        self.save()

    def set_speculative_match(self):
        related_matchups = PotentialMatchup.objects.filter(
            models.Q(participant1__in=[self.participant1, self.participant2]) |
            models.Q(participant2__in=[self.participant1, self.participant2])
        ).exclude(pk=self.pk).all()
        for matchup in related_matchups:
            matchup.manually_eliminated = True
            matchup.save()
        self.speculative_match = True
        self.manually_eliminated = False
        self.save()


    def unset_speculative_match(self):
        related_matchups = PotentialMatchup.objects.filter(
            models.Q(participant1__in=[self.participant1, self.participant2]) |
            models.Q(participant2__in=[self.participant1, self.participant2])
        ).exclude(pk=self.pk).all()
        for matchup in related_matchups:
            matchup.manually_eliminated = False
            matchup.save()
        self.speculative_match = False
        self.save()

    def manually_eliminate(self):
        self.unset_speculative_match()
        self.manually_eliminated = True
        self.save()

    def unset_manually_eliminate(self):
        self.manually_eliminated = False
        self.save()


    def __str__(self):
        return '{} + {}'.format(self.participant1, self.participant2)


class Matchup(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    matchup = models.ForeignKey(PotentialMatchup, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['week', 'matchup']

    def __str__(self):
        return '{}: {} + {}'.format(
            self.week,
            self.matchup.participant1,
            self.matchup.participant2
        )


class TruthBooth(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    matchup = models.ForeignKey(PotentialMatchup, on_delete=models.CASCADE)
    perfect_match = models.BooleanField(default=False)

    class Meta:
        unique_together = ['week', 'matchup']

    def __str__(self):
        return '{}: {} + {} = {}'.format(
            self.week,
            self.matchup.participant1,
            self.matchup.participant2,
            self.match
        )

    def save(self, *args, **kwargs):
        super(TruthBooth, self).save(*args, **kwargs)
        if self.perfect_match == True:
            self.matchup.set_perfect_match(match_type='truthbooth')
        else:
            self.matchup.eliminated_via_truthbooth = True
            self.matchup.save()

    def update(self, perfect_match):
        self.perfect_match = perfect_match
        self.save()

    @property
    def as_lists(self):
        return [[self.participant1, self.participant2], [self.participant2, self.participant1] ]

    @property
    def match(self):
        if self.perfect_match:
            return 'Perfect match'
        else:
            return 'No match'

    @classmethod
    def get_for_participants(cls, participant1, participant2):
        return cls.objects.filter(
            models.Q(
                models.Q(participant1=participant1) |
                models.Q(participant2=participant1)
            ) |
            models.Q(
                models.Q(participant1=participant2) |
                models.Q(participant2=participant2)
            )
        ).all()

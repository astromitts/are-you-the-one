from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views import View
from django.urls import reverse

from ayto.models import (
    Participant,
    PotentialMatchup,
    Week,
    Matchup,
    TruthBooth
)


class Base(View):
    def setup(self, request, *args, **kwargs):
        super(Base, self).setup(request, *args, **kwargs)
        self.weeks = Week.objects.order_by('week_number').all()
        self.reversed_weeks = Week.objects.order_by('-week_number').all()
        self.participants = Participant.objects.all()
        self.matchups = Matchup.objects.all()
        self.truthbooths = TruthBooth.objects.all()
        self.potential_matches = PotentialMatchup.objects.all()
        self.context = {
            'weeks': self.weeks,
            'reversed_weeks': self.reversed_weeks,
            'participants': self.participants,
            'matchups': self.matchups,
            'truthbooths': self.truthbooths,
            'potential_matches': self.potential_matches
        }


class MasterList(Base):
    def get(self, request, *args, **kwargs):
        self.context.update({
            'weeks_columns': self.weeks,
            'weeks_rows': Week.get_set_weeks()
        })
        template = loader.get_template('ayto/index.html')
        return HttpResponse(template.render(self.context, request))


class WeekOverlaps(Base):
    def get(self, request, *args, **kwargs):
        self.context.update({
            'weeks_columns': self.weeks,
            'weeks_rows': Week.objects.filter(
                week_number__lte=kwargs['week_number']).order_by('-week_number')
        })
        template = loader.get_template('ayto/index.html')
        return HttpResponse(template.render(self.context, request))


class ParticipantView(Base):
    def get(self, request, *args, **kwargs):
        template = loader.get_template('ayto/participant.html')
        participant = Participant.objects.get(url_slug=kwargs['participant_slug'])
        self.context.update({
            'participant': participant,
        })
        return HttpResponse(template.render(self.context, request))


class PotentialMatchupDetail(Base):
    def setup(self, request, *args, **kwargs):
        super(PotentialMatchupDetail, self).setup(request, *args, **kwargs)
        self.participant1 = Participant.objects.get(url_slug=kwargs['participant1_slug'])
        self.participant2 = Participant.objects.get(url_slug=kwargs['participant2_slug'])

        self.potential_matchup = PotentialMatchup.get(self.participant1, self.participant2)
        self.location = reverse(
            'pm_detail',
            kwargs={
                'participant1_slug': self.participant1.url_slug,
                'participant2_slug': self.participant2.url_slug
            }
        )

    def get(self, request, *args, **kwargs):
        template = loader.get_template('ayto/matchup_detail.html')

        self.context.update({
            'pm': self.potential_matchup,
        })
        return HttpResponse(template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        if 'set-perfect-match' in request.POST:
            self.potential_matchup.set_perfect_match('manual')
        elif 'unset-perfect-match' in request.POST:
            self.potential_matchup.unset_perfect_match()
        return redirect(self.location)



class WeekView(Base):
    def setup(self, request, *args, **kwargs):
        super(WeekView, self).setup(request, *args, **kwargs)
        self.week = Week.objects.get(week_number=kwargs['week_number'])
        self.location = reverse('week_index', kwargs={'week_number': self.week.week_number})
        self.available_participants = self.week.get_available_participants

    def get(self, request, *args, **kwargs):
        template = loader.get_template('ayto/week.html')
        self.context.update({
            'week': self.week,
            'available_participants': self.available_participants
        })
        return HttpResponse(template.render(self.context, request))

    def post(self, request, *args, **kwargs):
        if 'lock-match' in request.POST:
            participant1 = Participant.objects.get(pk=request.POST['participant1'])
            participant2 = Participant.objects.get(pk=request.POST['participant2'])
            if participant1 == participant2:
                messages.error(request, 'Match Participants need to be different people')
            else:
                source_matchup = PotentialMatchup.get(
                    participant1=participant1,
                    participant2=participant2
                )
                matchup = Matchup(week=self.week, matchup=source_matchup)
                matchup.save()
        elif 'lock-truthbooth' in request.POST:
            participant1 = Participant.objects.get(pk=request.POST['participant1'])
            participant2 = Participant.objects.get(pk=request.POST['participant2'])
            if participant1 == participant2:
                messages.error(request, 'Match Participants need to be different people')
            else:
                source_matchup = PotentialMatchup.get(
                    participant1=participant1,
                    participant2=participant2
                )
                truthbooth = TruthBooth(
                    week=self.week,
                    matchup=source_matchup,
                    perfect_match=request.POST.get('perfect_match') == 'Y'
                )
                truthbooth.save()
        elif 'lock-num-matches' in request.POST:
            self.week.matches_count = int(request.POST['num_matches'])
            self.week.save()
        elif 'undo-match' in request.POST:
            match = Matchup.objects.get(pk=request.POST['undo_match_pk'])
            match.delete()
        elif 'undo-truthbooth' in request.POST:
            match = TruthBooth.objects.get(pk=request.POST['undo_truthbooth_pk'])
            match.delete()

        return redirect(self.location)

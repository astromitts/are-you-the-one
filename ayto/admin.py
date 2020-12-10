from django.contrib import admin
from ayto.models import (
    Participant,
    Week,
    PotentialMatchup,
    Matchup,
    TruthBooth
)

admin.site.register(Participant)
admin.site.register(Week)
admin.site.register(PotentialMatchup)
admin.site.register(Matchup)
admin.site.register(TruthBooth)

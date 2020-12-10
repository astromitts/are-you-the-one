from django.contrib import admin
from django.urls import path
from ayto.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MasterList.as_view(), name='index'),
    path('participant/<int:participant_pk>', ParticipantView.as_view(), name='participant_index'),
    path('week/<int:week_number>', WeekView.as_view(), name='week_index'),
    path('potentialmatches/<int:pm_pk>', PotentialMatchupDetail.as_view(), name='pm_detail'),
]

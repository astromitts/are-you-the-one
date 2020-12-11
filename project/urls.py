from django.contrib import admin
from django.urls import path
from ayto.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MasterList.as_view(), name='index'),
    path('participant/<str:participant_slug>/', ParticipantView.as_view(), name='participant_index'),
    path('week/<int:week_number>/', WeekView.as_view(), name='week_index'),
    path('week/<int:week_number>/overlaps/', WeekOverlaps.as_view(), name='week_overlaps'),
    path('potentialmatches/<str:participant1_slug>/<str:participant2_slug>/', PotentialMatchupDetail.as_view(), name='pm_detail'),
]

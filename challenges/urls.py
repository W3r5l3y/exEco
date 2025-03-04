from django.urls import path
from .views import challenges_page, get_challenges, submit_challenge, assign_new_challenges

urlpatterns = [
    path('challenges/', challenges_page, name='challenges_page'),
    path('api/challenges/', get_challenges, name='get_challenges'),
    path('api/submit_challenge/', submit_challenge, name='submit_challenge'),
    path('api/assign_challenges/', assign_new_challenges, name='assign_challenges'),
]

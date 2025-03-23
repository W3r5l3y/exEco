from django.urls import path
from .views import contact_view, submit_contact_message

urlpatterns = [
    path("contact/", contact_view, name="contact"),
    path("submit/", submit_contact_message, name="submit_contact_message"),
]

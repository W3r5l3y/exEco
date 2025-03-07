from django.shortcuts import render
from qrscanner.models import Location

def gamekeeper_view(request):
    return render(request, 'gamekeeper/gamekeeper.html')


def add_location_to_qr(request, location_code, location_name, location_fact, cooldown_length):
    # Add relevant information for a qr code to the qrscanner database, then return a Json showing the new qr code location in media
    pass
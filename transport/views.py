from django.shortcuts import render

def transport_view(request):
    return render(request, "transport/transport.html")
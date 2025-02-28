from django.shortcuts import render

def garden_view(request):
    return render(request, 'garden/garden.html')
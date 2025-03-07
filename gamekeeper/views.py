from django.shortcuts import render

def gamekeeper_view(request):
    return render(request, 'gamekeeper/gamekeeper.html')
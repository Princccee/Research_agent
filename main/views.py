from django.http import HttpResponse

def welcome(request):
    return HttpResponse("Welcome to AI-research agent")

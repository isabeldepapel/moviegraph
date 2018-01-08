from django.shortcuts import render
from django.http import HttpResponse

from .graph import generate_graph


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. Scores index page.")

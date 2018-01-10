from django.shortcuts import render
from django.http import HttpResponse

from .graph import generate_graph
from .models import Name
from django.db.models import Q


# Create your views here.
def index(request):
    """View function for main/home page."""
    # generate graph of actors and movies
    # graph = generate_graph()
    actors = Name.objects.filter(
        Q(professions__icontains='actor') |
        Q(professions__icontains='actress')
    )
    context = {'actors': actors}
    return render(request, 'scores/index.html', context)
    #
    # return render(
    #     request,
    #     'scores/index.html',
    #     context
    # )
    # return HttpResponse("Hello, world. Scores index page.")


def submit(request):
    actors = context['actors']
    end_name = request.POST['end-name']
    match = actors.filter(primary_name__iexact=end_name)

    return HttpResponse('This is a stub: ' + end_name)

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
    return render(request, 'scores/index.html')

    # return HttpResponse("Hello, world. Scores index page.")


def submit(request):
    actors = Name.objects.filter(
        Q(professions__icontains='actor') |
        Q(professions__icontains='actress')
    )
    end_name = request.POST['end-name']
    match = actors.filter(primary_name__iexact=end_name)
    context = {}
    # check if no results
    if match.count() == 0:
        context['error_message'] = 'Not a valid name: ' + end_name
        return render(request, 'scores/index.html', context)
    else:
        actor = match[0]
        context['end_name'] = end_name
        context['actor_id'] = actor.id
        context['actor_name'] = actor.primary_name
        context['actor_birth_year'] = actor.birth_year
        context['actor_professions'] = actor.professions
        return render(request, 'scores/index.html', context)

    # return HttpResponse('This is a stub: ' + end_name)

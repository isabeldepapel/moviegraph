from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .graph import read_graph_from_csv
from .models import Name
from django.db.models import Q


# helper function
def capitalize(text):
    """Capitalize a given string."""
    text = text.strip()

    # if empty string, exit
    if len(text) < 1:
        return text

    s = text[0].upper()

    for i in range(1, len(text) - 1):
        # while not end of string or space or -
        pass


# Create your views here.
def index(request):
    """View function for main/home page."""
    # generate graph of actors and movies
    graph = read_graph_from_csv()
    context = {'graph': graph}

    return render(request, 'scores/index.html', context)

    # return HttpResponse("Hello, world. Scores index page.")


def validate_name(request):
    """
    Validate actor name exists in database before searching.

    If more than one name fits the criteria, selects the first one
    and returns the id.

    Won't render.
    """
    search_for = request.GET.get('search-for', None)
    print(request)
    print(request.GET)

    actor_list = Name.objects.filter(
        Q(primary_name=search_for) &
        Q(birth_year__isnull=False) &
        (Q(professions__icontains='actor') |
         Q(professions__icontains='actress'))
    )

    print(search_for)
    data = {}

    # TODO check if name in graph (if cached)
    if actor_list.count() == 0:
        data['error_message'] = 'Not a valid name.'
        data['status'] = 'false'
        print(JsonResponse)
        return JsonResponse(data, status=404)

    else:
        # grab first one in list
        actor = actor_list[0]
        data['actor_id'] = actor.id
        print(JsonResponse)
        return JsonResponse(data)


def score(request):
    """
    Search graph and calculate Bacon score.

    Returns a list of things to render.
    """


def submit(request):
    search_for = request.POST['search-for']

    # filter for name in actors/actresses
    match = Name.objects.filter(
        Q(primary_name=search_for) &
        (Q(professions__icontains='actor') |
         Q(professions__icontains='actress'))
    )
    # actors.filter(primary_name__iexact=end_name)
    context = {}
    # check if no results
    if match.count() == 0:
        context['error_message'] = 'Not a valid name: ' + search_for
        return render(request, 'scores/index.html', context)
    else:
        actor = match[0]
        context['search_for'] = search_for
        context['actor_id'] = actor.id
        context['actor_name'] = actor.primary_name
        context['actor_birth_year'] = actor.birth_year
        context['actor_professions'] = actor.professions
        return render(request, 'scores/index.html', context)

    # return HttpResponse('This is a stub: ' + end_name)

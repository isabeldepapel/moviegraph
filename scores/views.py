from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .graph import read_graph_from_csv, search_graph
from .models import Name
from django.db.models import Q

import string

# GRAPH = read_graph_from_csv()
# testing deploy
GRAPH = 10


# helper function
def capitalize(text):
    """
    Capitalize a given string.

    Uses python string lib, and then iterates through string to capitalize
    any letters following a hyphen or apostrophe.
    """
    # split on space and capitalize
    text = string.capwords(text)
    capitalized = ''

    # check for hyphen and apostrophe and capitalize
    # iterate through len - 1 because will capitalize at (i + 1)
    for i in range(len(text) - 1):
        capitalized += text[i]
        if text[i] == "-" or text[i] == "'":
            pass


# Create your views here.
def index(request):
    """View function for main/home page."""
    global GRAPH
    # generate graph of actors and movies
    # graph = read_graph_from_csv()

    return render(request, 'scores/index.html')

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
    if actor_list.count() == 0 or actor_list[0].id not in GRAPH:
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


def submit(request):
    search_for = request.GET['search-for']
    print(search_for)
    global GRAPH
    # filter for name in actors/actresses
    match = Name.objects.filter(
        Q(primary_name=search_for) &
        Q(birth_year__isnull=False) &
        (Q(professions__icontains='actor') |
         Q(professions__icontains='actress'))
    )

    context = {}
    # check if no results
    if match.count() == 0 or match[0].id not in GRAPH:
        context['error_message'] = 'Not a valid name: ' + search_for
        return render(request, 'scores/index.html', context)
    else:
        actor = match[0]
        # graph = read_graph_from_csv()
        print(GRAPH[actor.id])
        path = search_graph(GRAPH, actor.id)
        print(path)
        print(len(path))

        context['path'] = path
        context['search_for'] = actor

        return render(request, 'scores/index.html', context)

    # return HttpResponse('This is a stub: ' + end_name)

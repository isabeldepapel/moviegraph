from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .graph import read_graph_from_csv, search_graph, search_graph2
from .images import get_actor_image, get_movie_image
from .models import Name, Graph
from django.db.models import Q

# import string

testing = False
testing = True  # to test deploy
if testing:
    GRAPH = {}
else:
    GRAPH = read_graph_from_csv()
# testing deploy
# GRAPH = {}


# helper function
def capitalize(text):
    """
    Capitalize a given string.

    Uses strip and split to eliminate any excess space
    before/after and between text and then iterates
    through the new string to capitalize
    any letters following a hyphen or apostrophe.

    Input is always a string.

    Returns empty string if input is whitespace.
    """
    # trim whitespace and check for non-blank input
    text = text.strip()
    if len(text) < 1:
        return ''

    # split on space and capitalize
    words = text.split()
    new_text = []

    for word in words:
        if len(word) > 1:
            new_word = word[0].upper() + word[1:].lower()
        else:
            new_word = word[0].upper()
        new_text.append(new_word)
    text = ' '.join(new_text)

    # text = string.capwords(text)
    capitalized = ''

    to_upper = False  # tracks whether letter needs to be capitalized

    # check for hyphen and apostrophe and capitalize
    # iterate through len - 1 because will capitalize at (i + 1)
    for i in range(len(text)):
        if to_upper:
            capitalized += text[i].upper()
        else:
            capitalized += text[i]

        if text[i] == "-" or text[i] == "'":
            to_upper = True
        else:
            to_upper = False

    return capitalized


def get_images(path):
    """
    Get actor and movie images for the nodes and edges in the path.

    Takes in a list of tuples (actor, movie) and returns a list of
    dictionaries with actor and movies as the keys, and tuples (or
    a list of tuples for movies) of the form (actor/movie, image) as
    the values.
    """
    path_with_images = []

    for step in path:
        actor = step[0]
        movies = step[1]

        actor_info = (actor, get_actor_image(actor.primary_name))
        movies_info = [
            (movie, get_movie_image(movie.primary_title))
            for movie in movies
        ]

        path_with_images.append({'actor': actor_info, 'movies': movies_info})

    return path_with_images


def get_info(path):
    """
    Get actor and movie info for rendering as json.

    Takes in list of tuples (actor, movie) and returns a list of
    dictionaries with actor and movies as the keys, and tuples (or
    list of tuples for movies) of the form (actor/movie name, movie
    year, image) as the values.
    """
    path_with_images = []

    for step in path:
        actor = step[0]
        movies = step[1]

        actor_info = (
            actor.id,
            actor.primary_name,
            get_actor_image(actor.primary_name))
        movies_info = [
            (
                movie.id,
                movie.primary_title,
                movie.start_year,
                get_movie_image(movie.primary_title)
            )
            for movie in movies
        ]

        path_with_images.append({'actor': actor_info, 'movies': movies_info})

    return path_with_images


# Create your views here.
def index(request):
    """View function for main/home page."""
    global GRAPH
    # generate graph of actors and movies
    # graph = read_graph_from_csv()

    return render(request, 'scores/index.html')

    # return HttpResponse("Hello, world. Scores index page.")


def validate(request):
    """
    Validate actor name exists in database before searching.

    If more than one name fits the criteria, selects the first one
    and returns the id.

    Won't render.
    """
    search_for = capitalize(request.GET.get('search-for', default=''))
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


def search(request):
    print(request.GET)
    search_for = capitalize(request.GET.get('search-for', default=''))
    print(search_for)

    context = {}

    results = Name.objects.filter(
        Q(primary_name=search_for) &
        Q(birth_year__isnull=False) &
        (Q(professions__icontains='actor') |
         Q(professions__icontains='actress'))
    )

    print(results[0])
    print(results[0].id)
    # if not a valid name
    if results.count() == 0:
        context['error_message'] = 'Not a valid name: ' + search_for
        return render(request, 'scores/index.html', context)
    # if not in graph (e.g. tv actor)
    elif not Graph.objects.filter(star_id=results[0].id).exists():
        context['error_message'] = 'No data available for ' + search_for
        return render(request, 'scores/index.html', context)

    actor = results[0]
    path = search_graph2(actor.id)
    print(path)

    path_with_images = get_images(path)
    context['path'] = path_with_images
    # context['search_for'] = actor

    context['path_end'] = (
        actor,
        get_actor_image(actor.primary_name)
    )

    return render(request, 'scores/index.html', context)


def submit(request):
    print(request)
    print(request.GET)
    print(request.GET.get('search-for', default='test'))
    search_for = capitalize(request.GET.get('search-for', default=''))
    # search_for = capitalize(request.GET['search-for'])
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

        path_with_images = get_images(path)
        context['path'] = path_with_images
        # context['search_for'] = actor

        context['path_end'] = (
            actor,
            get_actor_image(actor.primary_name)
        )

        return render(request, 'scores/index.html', context)


# def submit(request):
#     search_for = request.GET.get('searchFor', default='')
#     print(search_for)
#     global GRAPH
#     # filter for name in actors/actresses
#     # match = Name.objects.filter(
#     #     Q(primary_name=search_for) &
#     #     Q(birth_year__isnull=False) &
#     #     (Q(professions__icontains='actor') |
#     #      Q(professions__icontains='actress'))
#     # )
#     #
#     # context = {}
#     data = {}
#
#     # check if no results
#     # if match.count() == 0 or match[0].id not in GRAPH:
#     #     data['error_message'] = 'Not a valid name: ' + search_for
#     #     return render(request, 'scores/index.html', context)
#     # else:
#     actor = Name.objects.get(id=search_for)
#     # graph = read_graph_from_csv()
#     # print(GRAPH[actor.id])
#     path = search_graph(GRAPH, actor.id)
#     print(path)
#     print(len(path))
#
#     path_with_images = get_info(path)
#     print(path_with_images)
#     data['path'] = path_with_images
#     # context['search_for'] = actor
#
#     data['path_end'] = (
#         actor.id,
#         actor.primary_name,
#         get_actor_image(actor.primary_name)
#     )
#
#     # return render(request, 'scores/index.html', context)
#     jr = JsonResponse(data)
#     print(jr)
#     return jr

    # return HttpResponse('This is a stub: ' + end_name)

def actors(request):
    search_for = capitalize(request.GET.get('name', default=''))
    print(search_for)
    # if search_for == '' or len(search_for) < 3:
    #     return {}

    actor_list = []
    actors = Name.objects.filter(
        Q(primary_name__startswith=search_for) &
        Q(birth_year__isnull=False) &
        (Q(professions__icontains='actor') |
         Q(professions__icontains='actress'))
    )[:20]

    for actor in actors:
        actor_list.append({
            'actor_id': actor.id,
            'actor_name': actor.primary_name
        })

    return JsonResponse({'actors': actor_list})

"""Index and search views (and their helper functions)."""

from django.shortcuts import render
from django.http import JsonResponse

from .graph import search_graph2, KEVIN_BACON_ID
from .images import get_actor_image, get_movie_image
from .models import Name
from django.db.models import Q


def get_actor(name):
    """
    Check whether a given name is in the graph table.

    Returns actor if found; else None.
    """
    name = name.lower()

    if name == 'kevin bacon':
        return Name.objects.get(id=KEVIN_BACON_ID)

    results = Name.objects.filter(
        Q(lowercase_name=name) &
        Q(in_graph=True)
    )
    try:
        actor = results[0]
        return actor
    except IndexError:
        return None


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


def index(request):
    """View function for main/home page."""
    return render(request, 'scores/index.html')


def validate(request):
    """
    Validate actor name exists in database before searching.

    If more than one name fits the criteria, selects the first one
    and returns the id.

    Won't render.
    """
    search_for = request.GET.get('search-for', default='')
    start_from = request.GET.get('start-from', default='')

    data = {}

    search_for_actor = get_actor(search_for)
    start_from_actor = get_actor(start_from)

    if not search_for_actor:
        data['errors'] = {'search-for': 'Not a valid name'}
    if not start_from_actor:
        data['errors'] = {'start-from': 'Not a valid name'}

    if 'errors' in data:
        data['status'] = 'false'
        return JsonResponse(data, status=404)
    else:
        data = {
            'search-for': search_for_actor.id,
            'start-from': start_from_actor.id,
        }
        return JsonResponse(data)


def search(request):
    """Search graph table using BFS to find Bacon score."""
    search_for = request.GET.get('search-for', default='')
    start_from = request.GET.get('start-from', default='')

    print(search_for)
    print(start_from)

    data = {}

    path = search_graph2(search_for, start_from)
    print(path)

    path_with_images = get_info(path)
    data['path'] = path_with_images

    name = Name.objects.get(id=search_for).primary_name
    data['path_end'] = (
        search_for,
        name,
        get_actor_image(name)
    )

    return JsonResponse(data)


def actors(request):
    """
    Return list of actors for datalist in app.js.

    View isn't rendered; only used to return json to app.js.
    """
    search_for = request.GET.get('name', default='').lower()
    LIMIT = 20

    actor_list = []
    actors = Name.objects.filter(
        Q(lowercase_name__startswith=search_for) &
        Q(birth_year__isnull=False) &
        (Q(professions__icontains='actor') |
         Q(professions__icontains='actress'))
    )[:LIMIT]

    # keep track of count to see whether to keep
    # making calls to /actors in app.js
    complete = False
    count = 0
    for actor in actors:
        actor_list.append({
            'actor_id': actor.id,
            'actor_name': actor.primary_name
        })
        count += 1

    if count < LIMIT:
        complete = True

    return JsonResponse({'actors': actor_list, 'complete': complete})

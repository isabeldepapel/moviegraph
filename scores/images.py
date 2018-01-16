"""
Gets image urls for actors and movies from TMDB.

Uses TMDBSimple API wrapper.

TMDBSimple doesn't return imdb ids, so results may not
always be an exact match. This retrieves the first result
from a list, on the premise that people will want the most
popular result.
"""

import tmdbsimple as tmdb
import environ

env = environ.Env()
env.read_env()

# assign API key
tmdb.API_KEY = env('TMDB_API_KEY')

BASE_URL = 'https://image.tmdb.org/t/p'
FILE_SIZE = '/w185'  # based on tmdb docs


def get_actor_id(name):
    """
    Get TMDB id for an actor based on their name.

    If more than one result (likely), fetches the
    first match. TMDB results are sorted by popularity,
    so first match is likely to be the one wanted.
    """
    search = tmdb.Search()
    search.person(query=name)

    # get id of first result
    tmdb_id = search.results[0]['id']
    return tmdb_id


def get_actor_image(name):
    """
    Get TMDB image url for an actor given their name.

    If more than one result (likely), gets the file path for
    the first person in the list. TMDB results are sorted by
    popularity, so first match is likely to be the one wanted.

    Returns the full image url.
    """
    search = tmdb.Search()
    search.person(query=name)

    # get profile image for first result
    file_path = search.results[0]['profile_path']

    return ''.join([BASE_URL, FILE_SIZE, file_path])


def get_movie_image(title):
    """
    Get TMDB image url for a movie given its name.

    If more than one result (likely), gets the file path for
    the first movie in the list.
    """
    search = tmdb.Search()
    search.movie(query=title)

    # get poster image for first result
    file_path = search.results[0]['poster_path']

    return ''.join([BASE_URL, FILE_SIZE, file_path])

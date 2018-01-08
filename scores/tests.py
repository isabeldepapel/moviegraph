from django.test import TestCase

from .graph import generate_graph
from .models import Title, Principal, Name


# Create your tests here.
MOVIES = range(3)

CAST = {0: ['a', 'b', 'c'],
        1: ['a', 'b'],
        2: ['d', 'e']}

GRAPH = {'a': {'b': set(0, 1), 'c': set(0)},
         'b': {'a': set(0, 1), 'c': set(0)},
         'c': {'a': set(0), 'b': set(0)},
         'd': {'e': set(2)},
         'e': {'e': set(2)}}


class GraphTests(TestCase):

    def test_each_movie_actor_is_a_node(self):
        """
        generate_graph creates one node for each movie actor.

        Doesn't take into account all actors (only those in movies).
        """
        movie_actors = set()

        movies = Title.objects.filter(title_type='movie')

        for movie in movies:
            cast = Principal.objects.filter(title_id=movie.id)
            cast = set([castperson.name_id for castperson in cast])
            movie_actors = movie_actors | cast

        num_actors = len(movie_actors)

        moviegraph = generate_graph()
        self.assertIs(len(moviegraph), num_actors)

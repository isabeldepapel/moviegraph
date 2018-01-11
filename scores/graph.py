"""
Generates a graph from the imdb data.

Default is only actors, and only movies.
"""

from django.db.models import Q
from .models import Title, Name, Principal
from collections import deque

import time
import csv
import environ

KEVIN_BACON = Name.objects.filter(
    Q(primary_name='Kevin Bacon') &
    Q(birth_year=1958)
)
KEVIN_BACON_ID = 'nm0000102'

DIR_PATH = environ.Path(__file__) - 1
FILE_PATH = str(DIR_PATH.path('data/graph_info.csv'))


def generate_graph():
    """
    Generate a graph represented as a dictionary.

    Actor ids as keys, vals are their neighbors (other actors).

    Parallel edges are stored as a dict within a dict:
    actor ids (neighbor nodes) are the keys, the movie ids in
    common (edges) are the values.
    """
    start = time.time()

    movies = Title.objects.filter(title_type='movie').values('id')
    # print(movies)

    graph = {}
    # iterate through movies, find actors for each and create nodes
    # for movie_id in movies.iterator():
    for movie in movies.iterator():
        movie_id = movie['id']
        # print(movie_id)
        # print(movie)
        actors = Principal.objects.filter(title_id=movie_id).values('name_id')
        # print(actors)
        # costars = set(actors)
        costars = set([actor['name_id'] for actor in actors])
        # print(costars)

        for actor in actors:
            # remove current actor from costars
            actor_id = actor['name_id']
            costars.remove(actor_id)
            # print(actor_id)
            # print(costars)

            # if no costars, go to next iteration
            if len(costars) < 1:
                continue

            # if actor not in graph:
            #     graph[actor] = costars
            # else:
            #     graph[actor] = graph[actor] | costars

            # if actor not in graph, add actor and its neighbors
            # with current movie as edge

            if actor_id not in graph:
                graph[actor_id] = {costar: set([movie_id]) for costar in costars}
            else:
                # check if costars are already neighbor nodes before adding
                for costar in costars:
                    if costar not in graph[actor_id]:
                        graph[actor_id][costar] = set([movie_id])
                    else:
                        graph[actor_id][costar].add(movie_id)

            # add current actor back to costars
            costars.add(actor_id)

    print(time.time() - start)
    print('it took {0:0.1f} seconds'.format(time.time() - start))
    return graph


def write_graph_to_csv(graph):
    """Write graph info to a csv to read from later."""
    start = time.time()

    with open(FILE_PATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        for actor_id, neighbors in graph.items():
            row = [actor_id]

            for neighbor_id, movies in neighbors.items():
                s = ''
                s += neighbor_id + ','
                s += ','.join(movie for movie in movies)
                row.append(s)

            writer.writerow(row)

    print(time.time() - start)
    print('it took {0:0.1f} seconds'.format(time.time() - start))


def read_graph_from_csv(file_name=FILE_PATH):
    """Create graph from csv file."""
    start = time.time()
    graph = {}

    with open(file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')

        for row in reader:
            actor_id = row[0]
            neighbors = [col.split(',') for col in row[1:]]

            graph[actor_id] = {}

            for neighbor in neighbors:
                costar_id = neighbor[0]
                movie_ids = neighbor[1:]

                graph[actor_id][costar_id] = set(movie_ids)

    print('it took {0:0.1f} seconds'.format(time.time() - start))
    return graph


def bfs(graph, start, end):
    """
    Perform BFS on given graph from start to end nodes.

    Start and end are given as name_ids.
    If there are multiple paths, returns one of them.

    Returns a dictionary where keys are actor_ids, and vals are the nodes
    that led there as a tuple of the form (actor_id, movie_id) to
    track the specific edge for recreating the path.
    """
    # initialize queue
    queue = deque()
    prev_nodes = {}  # keeps track of where you come from (recreate path)

    queue.append(start)

    while len(queue) > 0:
        current = queue.popleft()

        neighbors = graph[current]

        for neighbor in neighbors:
            # print(neighbor)
            # if neighbor hasn't been visited, add to queue
            # and mark the node you visit it from
            if neighbor not in prev_nodes:
                # add node you come from (and its edge)
                prev_nodes[neighbor] = (current, graph[current][neighbor])

                if neighbor == end:
                    return prev_nodes
                # add to queue
                queue.append(neighbor)

    return {}


def get_path(prev_nodes, start, end, reverse=False):
    """
    Return path from start to end node using prev_nodes generated by bfs.

    Reverse allows returning path in reverse in case Kevin Bacon (default)
    is changed to be end node. Allows for optimization by not rerunning graph.

    Returns a list of tuples of form (actor, movie(s))
    """
    prev = prev_nodes[end]
    actor = prev[0]
    movies = prev[1]
    path = deque()

    path.appendleft((actor, movies))

    # refactor to optimize with append/appendleft instead of reversing
    while actor != start:
        # path.appendleft((actor, movies))
        prev = prev_nodes[actor]
        actor = prev[0]
        movies = prev[1]
        path.appendleft((actor, movies))

    if reverse:
        path.reverse()

    return path


def search_graph(graph, search_for, start_from=KEVIN_BACON_ID):
    """
    Use bfs and get_path to search graph for given actor_id.

    Defaults to starting from Kevin Bacon.

    Returns a list of tuples of the form (name obj, title obj)
    """
    prev_nodes = bfs(graph, start_from, search_for)

    # if no possible path, return empty list
    if prev_nodes == {}:
        return []

    path_ids = get_path(prev_nodes, start_from, search_for)
    new_path = []

    # translate ids into objects
    for step in path_ids:
        actor_id = step[0]
        movie_ids = list(step[1])

        new_path.append(
            (Name.objects.get(id=actor_id),
             [Title.objects.get(id=movie_id) for movie_id in movie_ids])
        )

    return new_path

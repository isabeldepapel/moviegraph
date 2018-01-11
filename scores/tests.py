from django.test import TestCase

from .graph import bfs, get_path
from collections import deque

GRAPH1 = {
    0: {1: set('a'), 2: set('b')},
    1: {0: set('a')},
    2: {0: set('b')},
    3: {4: set('c')},  # nodes 3 & 4 not connected to other nodes
    4: {3: set('c')}
}

GRAPH2 = {
    0: {1: set(['a', 'x']), 2: set('b'), 3: set('b'), 4: set('a')},
    1: {0: set(['a', 'x']), 4: set('a'), 2: set('c')},
    2: {0: set('b'), 1: set('c'), 3: set('b')},
    3: {0: set('b'), 2: set('b'), 5: set('d')},
    4: {0: set('a'), 1: set('a')},
    5: {3: set('d')}
}


class GraphTests(TestCase):
    """Test bfs and find_path functions."""

    def test_bfs_finds_connected_node(self):
        """
        BFS returns dict of prev_nodes if found.

        Prev nodes is a dict where node is key, and tuple of node it came from
        and the edge name as its value.
        """
        result = bfs(GRAPH1, 0, 2)
        self.assertNotEqual(result, {})
        self.assertEqual(result[1], (0, set('a')))
        self.assertEqual(result[2], (0, set('b')))

    def test_bfs_doesnt_find_unconnected_node(self):
        """BFS returns empty dict if node not found."""
        result = bfs(GRAPH1, 0, 3)
        self.assertEqual(result, {})

    def test_get_path_returns_shortest_path(self):
        """Returns a list of tuples (node, edge) that recreate path."""
        path0_to_2 = get_path(bfs(GRAPH1, 0, 2), 0, 2)
        self.assertEqual(len(path0_to_2), 1)

        path1_to_2 = get_path(bfs(GRAPH1, 1, 2), 1, 2)
        self.assertEqual(len(path1_to_2), 2)

        expected_path = deque([(1, set('a')), (0, set('b'))])
        self.assertEqual(path1_to_2, expected_path)

        path4_to_2 = get_path(bfs(GRAPH2, 4, 2), 4, 2)
        self.assertEqual(len(path4_to_2), 2)

        path1_to_5 = get_path(bfs(GRAPH2, 1, 5), 1, 5)
        self.assertEqual(len(path1_to_5), 3)

"""Tests for graph module and helper function (capitalize) for views."""

from django.test import TestCase

from .graph import bfs, get_path
from .views import capitalize
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


class ViewTests(TestCase):
    """Tests capitalize helper function."""

    def test_capitalize_capitalizes_words(self):
        """
        Capitalizes one or multiple words in a string.

        Handles mixed case input.
        """
        cats = ['cat', 'CAT', 'cAt', 'CaT']
        cap_cat = 'Cat'

        for cat in cats:
            self.assertEqual(capitalize(cat), cap_cat)

        multi_words = 'quick brown fox jumped'
        cap_multi_words = 'Quick Brown Fox Jumped'

        self.assertEqual(capitalize(multi_words), cap_multi_words)

    def test_capitalize_strips_extra_spaces(self):
        """
        Trims leading and trailing whitespace.

        Also deletes extra whitespace between words.
        """
        words = ['   cat cow', '  cat cow  ', ' cat  cow']
        cap_words = 'Cat Cow'

        for word in words:
            self.assertEqual(capitalize(word), cap_words)

    def test_capitalize_capitalizes_after_hyphens(self):
        """
        Capitalizes following a hyphen.

        Works with multiple hyphens, but won't strip extra hyphens.
        """
        words = ['cat-cow', ' cat-cow  ']
        cap_words = 'Cat-Cow'

        for word in words:
            self.assertEqual(capitalize(word), cap_words)

        multi_hyphen = 'cat-cow-cat'
        cap_multi_hyphen = 'Cat-Cow-Cat'

        self.assertEqual(capitalize(multi_hyphen), cap_multi_hyphen)

        extra_hyphens = 'cat--cow'
        cap_extra_hyphens = 'Cat--Cow'

        self.assertEqual(capitalize(extra_hyphens), cap_extra_hyphens)

    def test_capitalize_capitalizes_after_apostrophes(self):
        """
        Capitalizes following an apostrophe.

        Works with multiple apostrophes, but won't strip extras.
        """
        words = ["o'toole", "  o'toole "]
        cap_words = "O'Toole"

        for word in words:
            self.assertEqual(capitalize(word), cap_words)

        multi_apost = "o'toole'toole"
        cap_multi_apost = "O'Toole'Toole"

        self.assertEqual(capitalize(multi_apost), cap_multi_apost)

        extra_apost = "o''toole"
        cap_extra_apost = "O''Toole"

        self.assertEqual(capitalize(extra_apost), cap_extra_apost)

    def test_capitalize_handles_blank_input(self):
        """
        Returns an empty string if given blank input.

        Handles empty string or multiple spaces.
        """
        blanks = ['', ' ', '     ']

        for blank in blanks:
            self.assertEqual(capitalize(blank), '')

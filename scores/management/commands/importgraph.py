"""Standalone script that will generate and write graph to a csv."""

from django.core.management.base import BaseCommand
from scores import graph


class Command(BaseCommand):
    """Add command line function to generate graph when calling manage.py."""

    help = 'Generates graph from database and writes to csv'

    def handle(self, *args, **options):
        """Generate graph."""
        new_graph = graph.generate_graph()
        return graph.write_graph_to_csv(new_graph)

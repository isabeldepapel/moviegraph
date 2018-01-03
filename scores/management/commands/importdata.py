"""Standalone script that will load data from imdb files into the app db."""

from django.core.management.base import BaseCommand, CommandError
from scores.models import (
    Title,
    Genre,
    TitleGenre,
    Name,
    Profession,
    NameProfession,
    Principal,
)

import csv
import environ

root = environ.Path(__file__) - 3
env = environ.Env()
env.read_env()

# set up file paths
TITLE_FILE = 'title.basics.tsv'
NAME_FILE = 'name.basics.tsv'
PRINCIPAL_FILE = 'title.principals.tsv'

# if in dev, load test data
if env('DEBUG'):
    print('debug')
    DATA_PATH = str(root.path('data/test/')) + '/'
else:
    DATA_PATH = str(root.path('data/')) + '/'

TITLE_PATH = DATA_PATH + TITLE_FILE
NAME_PATH = DATA_PATH + NAME_FILE
PRINCIPAL_PATH = DATA_PATH + PRINCIPAL_FILE


def load_titles():
    """Read title.basics.tsv into db."""
    print("loading titles")

    with open(TITLE_PATH, encoding='utf-8') as fd:
        rd = csv.reader(fd, delimiter="\t")
        for i, row in enumerate(rd):
            print(row)
            if(i > 15):
                break

    return None


class Command(BaseCommand):
    help = 'Reads IMDB data files into the database'

    def add_arguments(self, parser):
        """
        Parse arguments on command line.

        Requires file name or 'all' to load all files.
        Possible refactor to something easier than file names.
        """
        parser.add_argument(
            'file_name',
            help='File you want to load into database, or "all" to load all',
            type=str,
        )

    def handle(self, *args, **options):
        """
        Map file names to load functions.

        All will call all of the load fuctions.
        """

        print(options['file_name'])

        # OPTIONS
        # name.basics.tsv
        # title.basics.tsv
        # title.principals.tsv
        # all

        # all_entries = Title.objects.all()
        # for entry in all_entries:
        #     self.stdout.write('entry "%s"' % entry)
        load_titles()
        return None

    def load_names():
        """Read name.basics.tsv into db."""
        return None

    def load_principals():
        """Read title.principals.tsv into db."""
        return None

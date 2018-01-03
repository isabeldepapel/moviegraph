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
# env.read_env()

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


def convert_if_null(val):
    r"""Convert string '\N' to None to save as null in db."""
    if(val == "\\N"):
        val = None
    return val


def delete_records(model):
    """Drop all records from the specified model/table."""
    recs = model.objects.all()
    recs.delete()


def load_titles():
    """Read title.basics.tsv into db."""
    print("loading titles")

    # clear all existing recs from the models
    # delete_records(Title)
    # delete_records(Genre)
    # delete_records(TitleGenre)

    with open(TITLE_PATH, encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter="\t")

        for i, row in enumerate(reader):
            # tconst	titleType	primaryTitle	originalTitle	isAdult	startYear	endYear	runtimeMinutes	genres

            print(row['tconst'], row['titleType'], row['primaryTitle'], row['originalTitle'], row['isAdult'], row['startYear'], row['endYear'], row['runtimeMinutes'], row['genres'])

            title, created = Title.objects.get_or_create(
                id=row['tconst'],
                title_type=row['titleType'],
                primary_title=row['primaryTitle'],
                original_title=row['originalTitle'],
                is_adult=row['isAdult'],
                start_year=row['startYear'],
                end_year=convert_if_null(row['endYear']),
                runtime_minutes=convert_if_null(row['runtimeMinutes']),
            )

            print(title, created)

            genres = convert_if_null(row['genres'])

            if(genres):
                # add genres to genre table
                genres = genres.split(',')

                for genre in genres:
                    genre, created = Genre.objects.get_or_create(name=genre)

                    print(genre, created)

                    # add title's genres to TitleGenre join table
                    title_genre, created = TitleGenre.objects.get_or_create(
                        title=title,
                        genre=genre,
                    )

                    print(title_genre, created)

            if(i > 25):
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
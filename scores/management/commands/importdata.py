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

# for testing
# DATA_PATH = str(root.path('data/test/')) + '/'

# actual imdb data
DATA_PATH = str(root.path('data/')) + '/'

TITLE_PATH = DATA_PATH + TITLE_FILE
NAME_PATH = DATA_PATH + NAME_FILE
PRINCIPAL_PATH = DATA_PATH + PRINCIPAL_FILE


def convert_if_null(val):
    r"""Convert string '\N' to None to save as null in db."""
    if(val == "\\N"):
        val = None
    return val


def reset_tables():
    """Clear all records from all tables."""
    Title.objects.all().delete()
    Genre.objects.all().delete()
    TitleGenre.objects.all().delete()
    Name.objects.all().delete()
    Profession.objects.all().delete()
    NameProfession.objects.all().delete()
    Principal.objects.all().delete()


def load_titles():
    """Read title.basics.tsv into db."""
    print('loading titles')

    with open(TITLE_PATH, encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')

        for row in reader:
            title, created = Title.objects.get_or_create(
                id=row['tconst'],
                title_type=row['titleType'],
                primary_title=row['primaryTitle'],
                original_title=row['originalTitle'],
                is_adult=row['isAdult'],
                start_year=convert_if_null(row['startYear']),
                end_year=convert_if_null(row['endYear']),
                runtime_minutes=convert_if_null(row['runtimeMinutes']),
            )
            print(row)
            # print(title)

            genres = convert_if_null(row['genres'])

            if(genres):
                # add genres to genre table
                genres = genres.split(',')

                for genre in genres:
                    genre, created = Genre.objects.get_or_create(name=genre)

                    # add title's genres to TitleGenre join table
                    title_genre, created = TitleGenre.objects.get_or_create(
                        title=title,
                        genre=genre,
                    )
    return None


def load_names():
    """Read name.basics.tsv into db."""
    print('loading names')

    with open(NAME_PATH, encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')

        for row in reader:
            name, created = Name.objects.get_or_create(
                id=row['nconst'],
                primary_name=row['primaryName'],
                birth_year=row['birthYear'],
                death_year=convert_if_null(row['deathYear']),
            )
            print(name)

            professions = convert_if_null(row['primaryProfession'])

            if(professions):
                # add to profession table
                professions = professions.split(',')

                for prof in professions:
                    prof, created = Profession.objects.get_or_create(name=prof)

                    # add name, prof to NameProf table
                    name_prof, created = NameProfession.objects.get_or_create(
                        name=name,
                        profession=prof,
                    )
    return None


def load_principals():
    """Read title.principals.tsv into db."""
    print('loading principals')

    with open(PRINCIPAL_PATH, encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')

        for row in reader:
            cast_list = row['principalCast'].split(',')

            for cast_member in cast_list:
                # create entry, default to NOT known for
                # will update this later (iterate through names data)
                principal, created = Principal.objects.get_or_create(
                    name=Name.objects.get(id=cast_member),
                    title=Title.objects.get(id=row['tconst']),
                    known_for=False,
                )
    return None


def add_known_for_data():
    """Read known_for field from names.basics.tsv file into Principal table."""
    print('adding known_for data')

    # this may change as new movies are added, so set known_for to False
    # for all entries in table
    Principal.objects.all().update(known_for=False)

    with open(NAME_PATH, encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')

        for row in reader:
            known_for = row['knownForTitles']

            if(known_for):
                titles = known_for.split(',')

                for title_id in titles:
                    name_id = row['nconst']

                    Principal.objects.filter(
                        name_id=name_id,
                        title_id=title_id
                    ).update(known_for=True)


class Command(BaseCommand):
    help = 'Reads IMDB data files into the database'

    # def add_arguments(self, parser):
    #     """
    #     Parse arguments on command line.
    #
    #     Requires file name or 'all' to load all files.
    #     Possible refactor to something easier than file names.
    #     """
    #     parser.add_argument(
    #         'file_name',
    #         help='File you want to load into database, or "all" to load all',
    #         type=str,
    #     )

    def handle(self, *args, **options):
        """
        Map file names to load functions.

        All will call all of the load fuctions.
        """
        # print(options['file_name'])

        # reset_tables()
        load_titles()
        load_names()
        load_principals()
        add_known_for_data()
        return None

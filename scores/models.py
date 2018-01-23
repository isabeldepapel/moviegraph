"""
Set up models based on structure of IMDB data.

Modified Title and Name models by adding join tables for
TitleGenre and NameProfession to avoid storing arrays in
a single data field.

This will also simplify adding features in the future
(only search for actors, or exclude all tv shows, etc.).
"""

from django.db import models


# Create your models here.
class Title(models.Model):
    """Define title (movie, TV show, etc.) model."""

    id = models.CharField(max_length=9, primary_key=True)
    title_type = models.CharField(max_length=50)
    primary_title = models.TextField(null=True)
    original_title = models.TextField(null=True)
    is_adult = models.BooleanField()
    start_year = models.IntegerField(null=True)
    end_year = models.IntegerField(null=True)
    runtime_minutes = models.IntegerField(null=True)
    genres = models.TextField(null=True)

    def __str__(self):
        return self.primary_title + ', ' + str(self.start_year)


class Name(models.Model):
    id = models.CharField(max_length=9, primary_key=True)
    primary_name = models.CharField(db_index=True, max_length=200)
    birth_year = models.PositiveSmallIntegerField(null=True)
    death_year = models.PositiveSmallIntegerField(null=True)
    professions = models.TextField(null=True)
    known_for = models.TextField(null=True)
    in_graph = models.BooleanField(default=False)

    def __str__(self):
        return self.primary_name


class Principal(models.Model):
    """
    Join table for Name and Title.

    All the principal cast for a given title.

    Also includes field to indicate whether title is one for which
    the person is known.
    """

    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    name = models.ForeignKey(Name, on_delete=models.CASCADE)

    def __str__(self):
        s = str(self.name) + " in title: " + str(self.title)

        return s


class Graph(models.Model):
    """
    Table that contains graph info.

    Name, Costar, and all titles they have in common.
    """

    id = models.IntegerField(primary_key=True)
    star = models.ForeignKey(
        Name,
        on_delete=models.CASCADE,
        related_name='star'
    )
    costar = models.ForeignKey(
        Name,
        on_delete=models.CASCADE,
        related_name='costar'
    )
    titles = models.TextField()

    def __str__(self):
        s = str(self.star) + " with " + str(self.costar) + " in: "

        for title in self.titles.split(','):
            s += str(title)

        return s

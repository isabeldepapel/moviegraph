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
    """
    Define title (movie, TV show, etc.) model.

    Genres (in IMDB schema) pulled out into a separate join table.
    """

    id = models.CharField(max_length=9, primary_key=True)
    title_type = models.CharField(max_length=50)
    primary_title = models.TextField()
    original_title = models.TextField()
    is_adult = models.BooleanField()
    start_year = models.PositiveSmallIntegerField(null=True)
    end_year = models.PositiveSmallIntegerField(null=True)
    runtime_minutes = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return self.primary_title


class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    """
    Join table for Title and Genre.

    Up to 3 genres for each title.
    """

    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.title) + " has genre of " + str(self.genre)


class Name(models.Model):
    id = models.CharField(max_length=9, primary_key=True)
    primary_name = models.CharField(max_length=200)
    birth_year = models.PositiveSmallIntegerField()
    death_year = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return self.primary_name


class Profession(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class NameProfession(models.Model):
    """
    Join table for Name and Profession.

    Up to 3 professions for each name.
    """

    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name) + " has profession of " + str(self.profession)


class Principal(models.Model):
    """
    Join table for Name and Title.

    All the principal cast for a given title.

    Also includes field to indicate whether title is one for which
    the person is known.
    """

    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    known_for = models.BooleanField()

    def __str__(self):
        s = str(self.name) + " in title: " + str(self.title)
        s += " Known for title: " + str(self.known_for)

        return s

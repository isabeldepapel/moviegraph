# Generated by Django 2.0.1 on 2018-01-05 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scores', '0004_title_genres'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='end_year',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='title',
            name='runtime_minutes',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='title',
            name='start_year',
            field=models.FloatField(null=True),
        ),
    ]
# MovieGraph

Inspired by the [Six Degrees of Kevin Bacon](https://en.wikipedia.org/wiki/Six_Degrees_of_Kevin_Bacon) and [The Oracle of Bacon](https://oracleofbacon.org).

How many degrees of separation between two movie actors? MovieGraph creates a graph from available IMDb datasets and uses BFS to find the shortest path between two actors. Find it at http://movie-graph.com.

IMDb's datasets don't include images, so MovieGraph fetches images from TMDb using [tmdbsimple](https://github.com/celiao/tmdbsimple).

## IMDb data
Information on the available datasets can be found on their [website](http://www.imdb.com/interfaces/). TSV files (zipped) can be downloaded directly from https://datasets.imdbws.com/.

## Installation
1. Clone the repo and `cd` into the root project directory

1. Download the following datasets from IMDb into the data directory (`./scores/data`):
   - [name.basics.tsv.gz](https://datasets.imdbws.com/name.basics.tsv.gz)
   - [title.basics.tsv.gz](https://datasets.imdbws.com/title.basics.tsv.gz)
   - [title.principals.tsv.gz](https://datasets.imdbws.com/title.principals.tsv.gz)

1. Set up and activate a virtual environment. You can set one up with [Python 3](https://docs.python.org/3/library/venv.html): `python3 -m venv /path/to/virtual/env`

1. Install the project dependencies: `pip install -r requirements.txt`

1. Create a .env file in the moviegraph subdirectory (not the root project directory) to set up environment variables (`touch ./moviegraph/.env`) and add the following line to the file:

   `DEBUG=True`

   The `.env` file is read from both `settings.py` (in the same directory) and the scores app. This means when the scores app reads `.env`, it generates a warning that the `.env` file is in a different directory as the file that's reading it; you can ignore this. See [django-dotenv](https://github.com/jpadilla/django-dotenv) docs for more information.

1. Obtain a Django Secret Key using [MiniWebTool](https://www.miniwebtool.com/django-secret-key-generator/) and add it to your .env file:

   `SECRET_KEY=<secret key goes here>`

1. Obtain an API key from [TMDb](https://www.themoviedb.org/faq/api) and add it to your .env file:

   `TMDB_API_KEY=<api key goes here>`

1. Create a postgres database for the project ([Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04) has a good walkthrough of the process) and add it to your `.env` file:
   - Log into postgres: `psql`
   - Create a database: `CREATE DATABASE <databasename>;`
   - Create a user: `CREATE USER <user> WITH PASSWORD '<password>';`
   - Modify connection parameters for the user:
     - `ALTER ROLE <user> SET client_encoding TO 'utf8';`
     - `ALTER ROLE <user> SET default_transaction_isolation TO 'read committed';`
     - `ALTER ROLE <user> SET timezone TO 'UTC';`
   - Grant user access rights to the database: `GRANT ALL PRIVILEGES ON DATABASE <databasename> TO <user>;`
   - Grant user permission to create a database (for testing): `ALTER USER <user> CREATEDB;`
   - Add the database URL to `.env`:  
    `DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<databasename>`

1. Set up static files to run locally by commenting out the following line in `settings.py`:

   `STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'`

   MovieGraph is set up to load its static files from S3 for deployment. To continue using S3, specify the appropriate values for `AWS_STORAGE_BUCKET_NAME` and `AWS_S3_REGION_NAME` in `settings.py`. Also make sure to add the appropriate AWS access keys in `.env`:

   `AWS_ACCESS_KEY_ID=<access key id>`  
   `AWS_SECRET_ACCESS_KEY=<secret access key>`

   You'll also need to [configure your S3 bucket](https://www.caktusgroup.com/blog/2014/11/10/Using-Amazon-S3-to-store-your-Django-sites-static-and-media-files/) to allow access from the Django app.

1. Run migrations:
   - `python manage.py makemigrations`
   - `python manage.py migrate`

1. Load IMDb data from tsv files into the database:
   - `python manage.py importdata names`
   - `python manage.py importdata titles`
   - `python manage.py importdata principals`

   N.B. Because only partial datasets are available, some of the title ids and name ids in the join table are not found in the Name and Title tables when you try to import principals. If this happens, uncomment out the code in `load_principals()` that will check every entry and print out a set of bad name ids and a set of bad title ids and run the command to load principals (this takes about a day). Once this has completed, replace the existing constants, `BAD_NAMES` and `BAD_TITLES`, in `importdata.py` with the new information, comment out the code again, and then rerun the command.

1. Generate and load graph into the database:
   - Create a csv file of the graph, `graph.csv`, in the same directory as the tsv files:
      - `python manage.py importgraph`

   - Load the graph into the database by copying the csv file directly into postgres:
      - Log into postgres with `psql <databasename>` 
      - Run the following command:  
        `COPY scores_graph(id, star_id, costar_id, titles) FROM 'full/path/to/file.csv' WITH DELIMITER E'\t';`
   - Update the `in_graph` column in the Name table for those actors who are in the graph:
      - In postgres: `UPDATE scores_name SET in_graph=True WHERE scores_name.id IN (SELECT DISTINCT(star_id) FROM scores_graph);`

## Issues
1.  IMDb data only includes principal cast, not full cast, so Bacon scores won't always match (can be higher than) what you find on google or the Oracle of Bacon, etc.

2.  How do you find the right Emma Stone in IMDb?

    There's no good fix for this--right now, MovieGraph just searches for a movie actor named Emma Stone, whose birth date is not null, and then fetches the first result if there's more than one Emma Stone.

    Sorting by movie actors, and then not null birth dates means that there's often not more than one result returned, but this is still limiting. What if you wanted to expand the search beyond actors? Or what if you wanted the lesser known Emma Stone, who was in _White Angel_ (and who doesn't have a birth date in IMDb)?

3.  How do you find the right Emma Stone in TMDb (images)?

    Ideally, when pulling info from the API, you'd match against the IMDB id, but the tmdbsimple API wrapper doesn't return the IMDB ids for titles or names. It returns results based on popularity (so if there's more than one Spencer Tracy, MovieGraph assumes you're looking for the most famous/popular one).

    To fix this, MovieGraph would need to implement in its own API wrapper that incorporates the IMDb id strings into its interface. There's an existing API wrapper that does this, but it isn't compatible with Python 3.

# MovieGraph

Inspired by the [Six Degrees of Kevin Bacon](https://en.wikipedia.org/wiki/Six_Degrees_of_Kevin_Bacon) and [The Oracle of Bacon](https://oracleofbacon.org).

How many degrees of separation between two movie actors? MovieGraph creates a graph from available IMDb datasets and uses BFS to find the shortest path between two actors. Find it at [http://movie-graph.com].

IMDb's datasets don't include images, so MovieGraph fetches images from TMDb using [tmdbsimple](https://github.com/celiao/tmdbsimple).

## IMDb data
Information on the available datasets can be found on their [website](http://www.imdb.com/interfaces/). TSV files (zipped) can be downloaded directly from [https://datasets.imdbws.com/].

## Installation


## API key
You'll need an API key


## Set up virtual environment

- virtualenv
- Python 3 supports making virtualenv with python3 -m venv my-env
- to activate: In directory that contains my-env: source my-env/bin/activate

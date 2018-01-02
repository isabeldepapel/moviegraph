# Capstone Product Plan - Isabel Suchanek

## Personal Learning Goals

1.  Graph theory--specifically simple (no loops), undirected graphs with parallel edges and how best to represent them (adjacency list vs matrix). I'd also like to explore (if possible) dealing with weighted graphs, although the minimum viable product will focus on an unweighted graph.
2.  Efficiently processing large amounts of data--this will include finding an efficient way to generate a graph from data in a database, and then implementing BFS in order to find the shortest path between two nodes.
3.  Learning how to deploy a product so it will continue to operate while the back-end automatically updates itself on a regular schedule (downloading data from an external source).

## Problem Statement

This web app will calculate the Bacon score for any given actor entered by the user, or--if two names are entered--calculate the distance between those two actors and display the path. If I have time, I'd like to try weighting the graph by giving preference to the edges (movie titles) if they also are a work for which the actor is known (a list of max 4 in the IMDB dataset). I could also do the reverse to make the trivia a little more arcane.

## Market Research

A website already exists that does what I want to do (computes the Bacon score, and the score between any two actors) called the [Oracle of Bacon](https://oracleofbacon.org/). It has a lot of features beyond what I can complete in less than a month (searching based only on specific genres, specifying type of media to search (e.g. just movies or movies, reality TV, documentaries, etc.)). However, the website is pretty unattractive, both in terms of the general layout (especially the color palette) and, in particular, the way the path is displayed: actor names and movie titles (linking to the respective IMDB pages) in a colorful textbox.

I can't make the my web app any more efficient (especially because the [Oracle of Bacon](https://oracleofbacon.org/) written in C and implements caching in order to minimize running time), but I can make the interface more aesthetically pleasing. I'd like to use the TMDB API to pull actor profile images as the starting and end points for the path (and possibly for the intermediary actor nodes in the path). I might also look into using the API to pull up movie images for the movies connecting the actors, as well.

## User Personas

CS geek + movie nerd = <3. This is aimed at tech nerds who are interested in graphs and algorithms, as well as movies and movie trivia. The minimum viable product accomplishes this, but weighting the graph will tailor the app to my audience even more, both by making the graph and search functions more complex, but also by emphasizing the trivia aspect to highlight the movies for which the actor(s) is/are known.

## Trello Board

https://trello.com/invite/b/lxvgG04Y/3bacd41803c9a7930972fceaf36f1ac3/i-3-graphs


## Technology Selections

- Front end: jQuery
- Back end: Python and Django with a Postgres database
- Infrastructure: AWS to deploy


## Wireframe

- Work in progress:
![wireframe drawing]('./wireframe.jpg')

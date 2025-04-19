# Movie Finder

Uses themoviedb.org to look for new movies to watch and track those that you have seen.

## Setup

1. Copy sample.env to `movie_finder_app/.env`, update the API key and token
1. Create two lists in you themoviedb.org called 'Watched' and 'NeverWatch'
1. Navigate to the Watched list page and get the Account ID from the URL `https://www.themoviedb.org/list/[TMDB_ACCOUNT_ID]-watched`
1. Build and run the container

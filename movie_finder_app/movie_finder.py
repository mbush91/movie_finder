# movie_finder.py

import requests
import random
import webbrowser
from dotenv import load_dotenv
import os

load_dotenv()

# Replace with your TMDb API key
TMDB_API_KEY = os.environ["TMDB_API_KEY"]
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")
TMDB_ACCOUNT_ID = os.environ["TMDB_ACCOUNT_ID"]

# Define filtering criteria
FILTERS = {
    "min_num_ratings": 150,
    "release_date_min": "2020-01-01",  # Only movies released after this date
    "original_language": "en",
    "minimum_rating": 7.0,  # Minimum user rating
    "genres": [
        # ["Science Fiction","Romance"],
        ["Romance"]
    ],  # Genre to filter by
    "us_certification": "R",
}

# TMDb API endpoints
BASE_URL = "https://api.themoviedb.org/3"
GENRES_URL = f"{BASE_URL}/genre/movie/list"
DISCOVER_URL = f"{BASE_URL}/discover/movie"
MOVIELISTS_URL = f"{BASE_URL}/account/{TMDB_ACCOUNT_ID}/watchlist/movies"
MOVIEDETAIL_URL = f"{BASE_URL}/movie"

genre_ids = {}


def get_auth_header():
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
    }


def get_genres():
    global genre_ids

    if genre_ids == {}:
        response = requests.get(GENRES_URL, params={"api_key": TMDB_API_KEY})
        genre_ids = {g["id"]: g["name"] for g in response.json().get("genres", [])}

    return genre_ids


def get_genre_ids(genres):
    """Fetch genre ID based on genre name."""
    genre_ids = get_genres()

    genre_map = {v.lower(): k for k, v in genre_ids.items()}

    g_list = [str(genre_map[g.lower()]) for g in genres if g.lower() in genre_map]

    return ",".join(g_list)


def get_neverwatch_list():
    header = get_auth_header()
    response = requests.get(
        f"{BASE_URL}/account/{TMDB_ACCOUNT_ID}/lists", headers=header
    )

    list_id = -1
    for lst in response.json().get("results"):
        if lst["name"] == "NeverWatch":
            list_id = lst["id"]
            break

    # https://api.themoviedb.org/3/list/{list_id}/items
    url = f"{BASE_URL}/list/{list_id}"
    response = requests.get(url, headers=header)

    return {m["id"]: m for m in response.json().get("items", [])}


def get_watched_movies():
    header = get_auth_header()
    response = requests.get(
        f"{BASE_URL}/account/{TMDB_ACCOUNT_ID}/lists", headers=header
    )

    list_id = -1
    for lst in response.json().get("results"):
        if lst["name"] == "Watched":
            list_id = lst["id"]
            break

    # https://api.themoviedb.org/3/list/{list_id}/items
    url = f"{BASE_URL}/list/{list_id}"
    response = requests.get(url, headers=header)

    return {m["id"]: m for m in response.json().get("items", [])}


def add_to_watched(movie_id):
    header = get_auth_header()
    response = requests.get(
        f"{BASE_URL}/account/{TMDB_ACCOUNT_ID}/lists", headers=header
    )

    list_id = -1
    for lst in response.json().get("results"):
        if lst["name"] == "Watched":
            list_id = lst["id"]
            break

    # https://api.themoviedb.org/3/list/{list_id}/add_item
    url = f"{BASE_URL}/list/{list_id}/add_item"
    data = {"media_id": movie_id, "media_type": "movie"}
    requests.post(url, headers=header, json=data)


def add_to_neverwatch_list(movie_id):
    header = get_auth_header()
    response = requests.get(
        f"{BASE_URL}/account/{TMDB_ACCOUNT_ID}/lists", headers=header
    )

    list_id = -1
    for lst in response.json().get("results"):
        if lst["name"] == "NeverWatch":
            list_id = lst["id"]
            break

    # https://api.themoviedb.org/3/list/{list_id}/add_item
    url = f"{BASE_URL}/list/{list_id}/add_item"
    data = {"media_id": movie_id, "media_type": "movie"}
    requests.post(url, headers=header, json=data)


def discover_movies(filters: dict):
    movies = {}

    """Fetch movies based on filters."""
    params = {
        "api_key": TMDB_API_KEY,
        "include_adult": True,
        "language": "en-US",
        "sort_by": "vote_average.desc",  # Sort by best user ratings
        "page": 1,
    }

    if filters.get("min_num_ratings"):
        params["vote_count.gte"] = filters["min_num_ratings"]
    if filters.get("release_date_min"):
        params["primary_release_date.gte"] = filters["release_date_min"]
    if filters.get("original_language"):
        params["with_original_language"] = filters["original_language"]
    if filters.get("minimum_rating"):
        params["vote_average.gte"] = filters["minimum_rating"]
    if filters.get("us_certification"):
        params["certification_country"] = "US"
        params["region"] = "us"
        params["certification.gte"] = filters["us_certification"]

    if filters.get("genres"):
        for g in filters["genres"]:
            genres = get_genre_ids(g)
            params_with_genres = params.copy()
            params_with_genres["with_genres"] = genres
            response = requests.get(DISCOVER_URL, params=params_with_genres)
            movies.update({m["id"]: m for m in response.json().get("results", [])})
    else:
        response = requests.get(DISCOVER_URL, params=params)
        movies.update({m["id"]: m for m in response.json().get("results", [])})

    return {m["id"]: m for m in response.json().get("results", [])}


def discover_new_movies(filters: dict):
    movies = discover_movies(filters)
    watched = get_watched_movies()
    neverwatch = get_neverwatch_list()

    movies = {k: v for k, v in movies.items() if k not in watched}
    movies = {k: v for k, v in movies.items() if k not in neverwatch}

    return movies


def get_movie_details(movie_id):
    """Fetch detailed information about a movie."""
    response = requests.get(
        f"{MOVIEDETAIL_URL}/{movie_id}", params={"api_key": TMDB_API_KEY}
    )
    return response.json()


def get_parantal_rating(movie_id):
    """Fetch parental rating for a movie."""
    response = requests.get(
        f"{MOVIEDETAIL_URL}/{movie_id}/release_dates", params={"api_key": TMDB_API_KEY}
    )
    release_dates = response.json().get("results", [])

    for rd in release_dates:
        if rd["iso_3166_1"] == "US":
            for certification in rd["release_dates"]:
                if certification["certification"]:
                    return certification["certification"]

    return ""


def get_movie_trailer(movie_id):
    """Fetch movie trailer."""
    response = requests.get(
        f"{MOVIEDETAIL_URL}/{movie_id}/videos", params={"api_key": TMDB_API_KEY}
    )
    videos = response.json().get("results", [])

    for video in videos:
        if video["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={video['key']}"

    return ""


def get_streaming_info(movie_id):
    """Fetch streaming information for a movie."""
    response = requests.get(
        f"{MOVIEDETAIL_URL}/{movie_id}/watch/providers",
        params={"api_key": TMDB_API_KEY},
    )
    us_providers = response.json().get("results").get("US")
    providers = [f["provider_name"] for f in us_providers.get("flatrate", [])]

    if providers == []:
        providers = [f"r-{f['provider_name']}" for f in us_providers.get("rent", [])]

    return ", ".join(providers)


def main():
    global genre_ids

    movies = discover_new_movies(FILTERS)

    if not movies:
        print("No suitable movies found. Try adjusting filters.")
        return
    else:
        print(f"Found {len(movies)} movies that match your criteria.")

    if genre_ids == {}:
        get_genre_ids([])

    while True:
        # Pick a random movie from the filtered list
        movie = random.choice(list(movies.values()))
        title = movie["title"]
        movie_id = movie["id"]
        movie_genres = [genre_ids[g] for g in movie["genre_ids"]]
        description = movie.get("overview", "No description available.")
        parental_rating = get_parantal_rating(movie_id)
        url = f"https://www.themoviedb.org/movie/{movie_id}"

        get_movie_details(movie_id)
        streaming_info = get_streaming_info(movie_id)

        print(f"🎬 Movie Recommendation: [{parental_rating}] {title}")
        print(f"🎭 Genres: {', '.join(movie_genres)}")
        print(f"🌟 User Rating: {movie['vote_average']}")
        print(f"📅 Release Date: {movie['release_date']}")
        print(f"📝 Description: {description}")
        print(f"🔗 Link: {url}")
        print(f"📺 Streaming on: {streaming_info}")

        while True:
            action = (
                input(
                    "Choose an option [(y)es/(o)pen/(t)railer/(s)een/(n)ext/(x)neverwatch/(q)uit]: "
                )
                .strip()
                .lower()
            )
            if action == "y":
                webbrowser.open(url)
                return
            elif action == "o":
                webbrowser.open(url)
            elif action == "t":
                trailer_url = get_movie_trailer(movie_id)
                if trailer_url:
                    webbrowser.open(get_movie_trailer(movie_id))
                else:
                    print("No trailer available.")
            elif action == "s":
                add_to_watched(movie_id)
                movies.pop(movie_id)
                break
            elif action == "x":
                add_to_neverwatch_list(movie_id)
                break
            elif action == "n":
                movies.pop(movie_id)
                break
            elif action == "q":
                return


if __name__ == "__main__":
    main()

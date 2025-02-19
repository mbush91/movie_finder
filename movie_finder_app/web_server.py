# web_server.py

from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
from movie_finder import (
    discover_new_movies,
    get_genre_ids,
    add_to_watched,
    add_to_neverwatch_list,
    get_movie_trailer,
)

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/discover", methods=["GET"])
def discover_movies_endpoint():
    filters = {
        "min_num_ratings": int(request.args.get("min_votes", 150)),
        "release_date_min": request.args.get("release_date", "2020-01-01"),
        "original_language": request.args.get("original_language", "en"),
        "minimum_rating": float(request.args.get("min_rating", 7.0)),
        "us_certification": request.args.get("us_certification", "R"),
    }

    # Handle multiple genres
    selected_genres = request.args.getlist("genre[]")  # Get multiple genres as a list
    genre_ids = get_genre_ids(selected_genres)
    if genre_ids:
        filters["genres"] = [
            selected_genres
        ]  # Wrap in an extra list to match `movie_finder.py` structure

    movies = discover_new_movies(filters)
    return jsonify(
        list(movies.values())
    )  # Convert dictionary to list for JSON response


@app.route("/mark_watched", methods=["POST"])
def mark_watched():
    movie_id = request.json.get("movie_id")
    if movie_id:
        add_to_watched(movie_id)
        return jsonify({"success": True, "message": "Movie marked as watched."})
    return jsonify({"success": False, "message": "Invalid movie ID."}), 400


@app.route("/mark_neverwatch", methods=["POST"])
def mark_neverwatch():
    movie_id = request.json.get("movie_id")
    if movie_id:
        add_to_neverwatch_list(movie_id)
        return jsonify({"success": True, "message": "Movie added to Never Watch list."})
    return jsonify({"success": False, "message": "Invalid movie ID."}), 400


@app.route("/get_trailer", methods=["GET"])
def get_trailer():
    movie_id = request.args.get("movie_id")
    if movie_id:
        trailer_url = get_movie_trailer(movie_id)
        if trailer_url:
            return jsonify({"success": True, "trailer_url": trailer_url})
        return jsonify({"success": False, "message": "No trailer found."}), 404
    return jsonify({"success": False, "message": "Invalid movie ID."}), 400


if __name__ == "__main__":
    dbg = os.getenv("FLASK_ENV") == "development"
    app.run(debug=dbg, host="192.168.1.102", port=5321)

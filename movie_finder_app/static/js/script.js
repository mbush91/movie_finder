/**
 * script.js
 */

$(document).ready(function () {
    let movies = [];
    let currentIndex = 2;

    $("#filter-form").on("submit", function (event) {
        event.preventDefault();
        fetchMovies();
    });

    function fetchMovies() {
        let selectedGenres = $("#genre").val() || [];
        let min_rating = $("#min_rating").val();
        let min_votes = $("#min_votes").val();
        let release_date = $("#release_date").val();
        let us_certification = $("#us_certification").val(); // New dropdown value

        $.getJSON("/discover", {
            "genre[]": selectedGenres,
            min_rating,
            min_votes,
            release_date,
            us_certification   // Pass the parental rating to the backend
        }, function (data) {
            if (data.length === 0) {
                alert("No movies found.");
                $(".carousel-container").addClass("d-none");
                return;
            }

            movies = data;
            currentIndex = Math.min(2, movies.length - 1);
            $(".carousel-container").removeClass("d-none");
            updateCarousel();
        });
    }

    function updateCarousel() {
        let movieWrapper = $(".movie-wrapper").empty();
        let start = Math.max(0, currentIndex - 2);
        let end = Math.min(movies.length, currentIndex + 3);

        for (let i = start; i < end; i++) {
            let movie = movies[i];
            let posterPath = movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : "https://via.placeholder.com/500x750?text=No+Image";
            let cardClass = i === currentIndex ? "movie-card center" : "movie-card";

            movieWrapper.append(`
                <div class="${cardClass}" data-index="${i}" data-id="${movie.id}">
                    <img src="${posterPath}" alt="${movie.title}">
                    <div class="movie-details">
                        <h5>${movie.title}</h5>
                        ${i === currentIndex ? `
                        <div class="movie-buttons">
                            <a href="https://www.themoviedb.org/movie/${movie.id}" class="btn btn-primary" target="_blank">More Info</a>
                            <button class="btn btn-success mark-watched" data-id="${movie.id}">Watched</button>
                            <button class="btn btn-danger mark-neverwatch" data-id="${movie.id}">Never Watch</button>
                            <button class="btn btn-warning watch-trailer" data-id="${movie.id}">Trailer</button>
                        </div>
                        ` : ""}
                    </div>
                </div>
            `);
        }
    }

    // Event listeners for Previous and Next buttons
    $(document).on("click", "#prev", function () {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });

    $(document).on("click", "#next", function () {
        if (currentIndex < movies.length - 1) {
            currentIndex++;
            updateCarousel();
        }
    });

    // Event listener for Watched button
    $(document).on("click", ".mark-watched", function () {
        let movieId = $(this).data("id");
        $.ajax({
            url: "/mark_watched",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ movie_id: movieId }),
            success: function (response) {
                alert(response.message);
            },
            error: function (error) {
                alert("Error marking movie as watched.");
            }
        });
    });

    // Event listener for Never Watch button
    $(document).on("click", ".mark-neverwatch", function () {
        let movieId = $(this).data("id");
        $.ajax({
            url: "/mark_neverwatch",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ movie_id: movieId }),
            success: function (response) {
                alert(response.message);
            },
            error: function (error) {
                alert("Error adding movie to Never Watch list.");
            }
        });
    });

    // Event listener for Trailer button
    $(document).on("click", ".watch-trailer", function () {
        let movieId = $(this).data("id");
        $.ajax({
            url: "/get_trailer",
            type: "GET",
            data: { movie_id: movieId },
            success: function (response) {
                if (response.success) {
                    window.open(response.trailer_url, "_blank");
                } else {
                    alert(response.message);
                }
            },
            error: function () {
                alert("Trailer not found.");
            }
        });
    });
});

from flask import Flask, request, render_template, jsonify, session, redirect
import pickle
import requests

app = Flask(__name__)
app.secret_key = "mysecret123"   # 👈 HERE

# 📦 Load data
movies = pickle.load(open("C:/moviee/movies.pkl", "rb"))
similarity = pickle.load(open("C:/moviee/similarity.pkl", "rb"))

# 🔑 API Key
API_KEY = "ba6c7329be25708434b32e6678c129ad"


# 🌐 Safe API call
def safe_request(url):
    try:
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return {}


# 🎥 Fetch movie details
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        data = safe_request(url)

        poster = data.get("poster_path")
        rating = data.get("vote_average")
        overview = data.get("overview") or "No description available"

        poster_url = (
            "https://image.tmdb.org/t/p/w500/" + poster
            if poster else
            "https://via.placeholder.com/200x300?text=No+Image"
        )

        return poster_url, rating, overview

    except:
        return "https://via.placeholder.com/200x300", "N/A", "No description"


# 🎯 Recommendation
def recommend(user_input):
    if not user_input:
        return []

    user_input = user_input.lower()
    result = []
    LIMIT = 12

    # 🎭 Genre search
    genres_list = ["action", "comedy", "drama", "romance", "thriller", "horror"]

    if any(g in user_input for g in genres_list):
        filtered = movies[movies['genres'].astype(str).str.lower().str.contains(user_input)]

        for i in range(min(LIMIT, len(filtered))):
            row = filtered.iloc[i]
            poster, rating, overview = fetch_movie_details(row.movie_id)

            result.append({
                "title": row.title,
                "poster": poster,
                "rating": rating,
                "overview": overview
            })
        return result

    # 📺 Series search
    if "series" in user_input:
        url = f"https://api.themoviedb.org/3/trending/tv/day?api_key={API_KEY}"
        data = safe_request(url)

        for show in data.get("results", [])[:LIMIT]:
            poster = show.get("poster_path")
            poster_url = (
                "https://image.tmdb.org/t/p/w500/" + poster
                if poster else
                "https://via.placeholder.com/200x300"
            )

            result.append({
                "title": show.get("name"),
                "poster": poster_url,
                "rating": show.get("vote_average"),
                "overview": show.get("overview") or "No description available"
            })
        return result

    # 🎬 ML movie search
    matched = movies[movies['title'].str.lower().str.contains(user_input)]

    if not matched.empty:
        index = matched.index[0]
        distances = similarity[index]

        movie_list = sorted(list(enumerate(distances)),
                            reverse=True, key=lambda x: x[1])[1:LIMIT+1]

        for i in movie_list:
            row = movies.iloc[i[0]]
            poster, rating, overview = fetch_movie_details(row.movie_id)

            result.append({
                "title": row.title,
                "poster": poster,
                "rating": rating,
                "overview": overview
            })
        return result

    # 🌐 Fallback search
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={user_input}"
    data = safe_request(url)

    for movie in data.get("results", [])[:LIMIT]:
        poster = movie.get("poster_path")
        poster_url = (
            "https://image.tmdb.org/t/p/w500/" + poster
            if poster else
            "https://via.placeholder.com/200x300"
        )

        result.append({
            "title": movie.get("title"),
            "poster": poster_url,
            "rating": movie.get("vote_average"),
            "overview": movie.get("overview") or "No description available"
        })

    return result


# 🔗 API (for JS fetch)
@app.route("/recommend", methods=["GET"])
def api_recommend():
    movie = request.args.get("movie")

    if not movie:
        return jsonify({"error": "Movie parameter missing"})

    return jsonify(recommend(movie))


# 🔐 LOGIN PAGE
@app.route("/")
def login_page():
    return render_template("login.html")

# 🏠 HOME PAGE
@app.route("/home", methods=["GET", "POST"])
def home():
    movie_data = []
    message = ""

    banner_movies = recommend("action")[:5]
    trending_movies = recommend("action")
    top_rated = recommend("drama")
    comedy_movies = recommend("comedy")
    horror_movies = recommend("horror")
    bollywood_movies = recommend("hindi")

    if request.method == "POST":
        movie = request.form.get("movie")
        movie_data = recommend(movie)

        if not movie_data:
            message = "❌ Movie not found"

    return render_template(
        "index.html",
        movie_data=movie_data,
        banner_movies=banner_movies,
        trending_movies=trending_movies,
        top_rated=top_rated,
        comedy_movies=comedy_movies,
        horror_movies=horror_movies,
        bollywood_movies=bollywood_movies,
        message=message,
        active="home"
    )


# 🎬 MOVIES PAGE
@app.route("/movies", methods=["GET", "POST"])
def movies_page():
    movie_data = []
    message = ""

    if request.method == "POST":
        query = request.form.get("movie")
        movie_data = recommend(query)
    else:
        movie_data = recommend("action")

    if not movie_data:
        movie_data = []
        message = "❌ No movies found"

    return render_template(
        "movies.html",
        movie_data=movie_data,
        message=message,
        active="movies"
    )


# 📺 SERIES PAGE
@app.route("/series", methods=["GET", "POST"])
def series_page():
    movie_data = []
    message = ""

    if request.method == "POST":
        query = request.form.get("movie")
        movie_data = recommend("series " + query)
    else:
        movie_data = recommend("series")

    if not movie_data:
        movie_data = []
        message = "❌ No series found"

    return render_template(
        "series.html",
        movie_data=movie_data,
        message=message,
        active="series"
    )

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ▶ RUN
if __name__ == "__main__":
    app.run(debug=True)
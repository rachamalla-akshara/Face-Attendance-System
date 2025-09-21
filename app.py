from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import os

app = Flask(__name__, template_folder="templates")

OMDB_API_KEY = "9fccdcbb"

movies = pd.read_csv("../data/movies_list.csv")
movies['combined_features'] = (
    movies['title'].astype(str) + " " +
    movies['genres'].astype(str) + " " +
    movies['description'].astype(str)
)

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['combined_features'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

def fetch_movie_details(movie_name):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_name}"
    response = requests.get(url).json()
    if response.get("Response") == "True":
        return {
            "title": response.get("Title"),
            "year": response.get("Year"),
            "poster": response.get("Poster") if response.get("Poster") != "N/A" else None,
            "rating": response.get("imdbRating")
        }
    return {
        "title": movie_name,
        "year": "N/A",
        "poster": None,
        "rating": "N/A"
    }

def get_recommendations(movie_name, top_n=5):
    matches = movies.index[movies['title'].str.lower() == movie_name.lower()].tolist()
    if not matches:
        return [{"title": "Movie not found.", "poster": None, "year": "N/A", "rating": "N/A"}]
    idx = matches[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    movie_indices = [i[0] for i in sim_scores]
    recommendations = []
    for title in movies['title'].iloc[movie_indices].tolist():
        recommendations.append(fetch_movie_details(title))
    return recommendations

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    movie_name = request.form.get("movie_name")
    recommendations = get_recommendations(movie_name)
    return render_template("recommendations.html", movie=movie_name, recommendations=recommendations)

if __name__ == "__main__":
    print("Looking for templates in:", os.path.abspath("templates"))
    app.run(debug=True)

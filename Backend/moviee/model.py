import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast

# Load datasets
movies = pd.read_csv(r"C:/moviee/tmdb_5000_movies.csv")
credits = pd.read_csv(r"C:/moviee/tmdb_5000_credits.csv")

# Merge
movies = movies.merge(credits, on='title')

# Select important columns
movies = movies[['movie_id','title','overview','genres','keywords','cast','crew']]


# Drop null
movies.dropna(inplace=True)

# Convert JSON columns
def convert(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name'])
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

# Combine tags
movies['tags'] = movies['overview'] + " " + movies['genres'].astype(str) + " " + movies['keywords'].astype(str)

# Lowercase
movies['tags'] = movies['tags'].apply(lambda x: x.lower())

# Vectorization
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(movies['tags']).toarray()

# Similarity
similarity = cosine_similarity(vectors)

# Save
pickle.dump(movies, open("movies.pkl", "wb"))
pickle.dump(similarity, open("similarity.pkl", "wb"))

print("✅ Perfect model ready")
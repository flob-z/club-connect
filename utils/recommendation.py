import mysql.connector
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Database connection function
def connect_db():
    return mysql.connector.connect(
        host="localhost",  # e.g., "localhost"
        user="root",
        password="",
        database="clubsdb"
    )

# Fetch data from database
def fetch_data(query):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(query)
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return pd.DataFrame(data)

# Load data from MySQL
clubs = fetch_data("SELECT id AS club_id, name, description, category FROM clubs")
users = fetch_data("SELECT id AS user_id, name FROM users")
ratings = fetch_data("SELECT user_id, club_id, rating FROM club_ratings")

# Remove duplicates and missing values
ratings = ratings.drop_duplicates(subset=['user_id', 'club_id'])
ratings.dropna(subset=['rating'], inplace=True)
ratings['rating'] = pd.to_numeric(ratings['rating'], errors='coerce')

# 📌 Popularity-Based Recommendation System
ratings_with_name = ratings.merge(clubs, on='club_id')

# Compute number and average of ratings per club
num_ratings_df = ratings_with_name.groupby('name').count()['rating'].reset_index()
num_ratings_df.rename(columns={'rating': 'num_ratings'}, inplace=True)

avg_ratings_df = ratings_with_name.groupby('name').mean(numeric_only=True)['rating'].reset_index()
avg_ratings_df.rename(columns={'rating': 'avg_rating'}, inplace=True)

# Merge and filter clubs with at least 5 ratings
popular_clubs = num_ratings_df.merge(avg_ratings_df, on='name')
popular_clubs = popular_clubs[popular_clubs['num_ratings'] >= 3].sort_values('avg_rating', ascending=False)

if popular_clubs.empty:
    print("No popular clubs found. Adjust thresholds or check the dataset.")
else:
    print(f"Popular clubs found: {popular_clubs.shape[0]}")
    print(popular_clubs.head())

# 📌 Collaborative Filtering-Based Recommender System
# Filter active users (who rated at least 2 clubs)
active_users = ratings.groupby('user_id').count()['rating'] >= 2
active_users = active_users[active_users].index

filtered_ratings = ratings[ratings['user_id'].isin(active_users)]

# Filter popular clubs (rated by at least 2 users)
popular_clubs = filtered_ratings.groupby('club_id').count()['rating'] >= 2
popular_clubs = popular_clubs[popular_clubs].index

final_ratings = filtered_ratings[filtered_ratings['club_id'].isin(popular_clubs)]

# Create pivot table (User-Club Matrix)
pt = final_ratings.pivot_table(index='club_id', columns='user_id', values='rating', fill_value=0)

if pt.empty:
    print("Pivot table is empty. No collaborative filtering can be performed.")
else:
    print(f"Pivot table shape: {pt.shape}")

    # Compute similarity scores using cosine similarity
    similarity_scores = cosine_similarity(pt)

    # 📌 Recommendation function
    def recommend(club_name):
        club_name = club_name.strip().lower()
        clubs['name'] = clubs['name'].str.strip().str.lower()

        if club_name not in clubs['name'].values:
            return f"Club '{club_name}' not found in the dataset."

        club_id = clubs[clubs['name'] == club_name]['club_id'].values[0]

        if club_id not in pt.index:
            return f"Club '{club_name}' not found in the pivot table."

        index = list(pt.index).index(club_id)
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

        data = []
        for item_index, score in similar_items:
            similar_club_id = pt.index[item_index]
            temp_df = clubs[clubs['club_id'] == similar_club_id]
            if not temp_df.empty:
                item = temp_df[['name', 'description', 'category']].drop_duplicates().values.flatten().tolist()
                if item not in data:
                    data.append(item)

        if not data:
            return f"No recommendations found for '{club_name}'."
        return data

    # Test the recommendation function
    print("\nRecommendations for 'Tech Club':", recommend('Pharmacy Students Association'))

    # Save data for later use
    pickle.dump(popular_clubs, open('popular_clubs.pkl', 'wb'))
    pickle.dump(pt, open('pt.pkl', 'wb'))
    pickle.dump(clubs.drop_duplicates('name'), open('clubs.pkl', 'wb'))
    pickle.dump(similarity_scores, open('similarity_scores.pkl', 'wb'))

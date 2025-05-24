from flask import Blueprint, jsonify
from db import get_db_connection

recommendation_routes = Blueprint('recommendation_routes', __name__)

def recommend_clubs(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Example Query: Fetch clubs based on user interests
    cursor.execute("""
        SELECT c.id, c.name, c.description 
        FROM clubs c
        JOIN user_interests ui ON c.category = ui.category
        WHERE ui.user_id = %s
        LIMIT 5
    """, (user_id,))
    
    clubs = cursor.fetchall()
    conn.close()

    return [{'id': row[0], 'name': row[1], 'description': row[2]} for row in clubs]

@recommendation_routes.route('/recommend/<int:user_id>', methods=['GET'])
def recommend(user_id):
    recommendations = recommend_clubs(user_id)
    return jsonify(recommendations)

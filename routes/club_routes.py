from flask import Blueprint, request, jsonify
from db import get_db_connection

club_routes = Blueprint('club_routes', __name__)

@club_routes.route('/clubs', methods=['GET'])
def get_clubs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clubs")
    clubs = cursor.fetchall()
    conn.close()
    
    return jsonify([{'id': row[0], 'name': row[1], 'category': row[2]} for row in clubs])

@club_routes.route('/club', methods=['POST'])
def add_club():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clubs (name, category) VALUES (%s, %s)", (data['name'], data['category']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Club added successfully!'}), 201

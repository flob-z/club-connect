from flask import Blueprint, request, jsonify
from db import get_db_connection

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return jsonify([{'id': row[0], 'name': row[1]} for row in users])

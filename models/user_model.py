import MySQLdb
from config import DB_CONFIG

def get_db_connection():
    return MySQLdb.connect(**DB_CONFIG)

class User:
    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        return user

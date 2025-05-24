import MySQLdb
from config import DB_CONFIG

def get_db_connection():
    return MySQLdb.connect(**DB_CONFIG)

class Club:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clubs")
        clubs = cursor.fetchall()
        conn.close()
        return clubs

    @staticmethod
    def get_by_id(club_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clubs WHERE id = %s", (club_id,))
        club = cursor.fetchone()
        conn.close()
        return club

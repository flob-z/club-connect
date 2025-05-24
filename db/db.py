import MySQLdb
from config import DB_CONFIG

def get_db_connection():
    return MySQLdb.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        passwd=DB_CONFIG['password'],
        db=DB_CONFIG['database']
    )

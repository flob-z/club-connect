import mysql.connector
import pandas as pd

# Database connection function
def connect_db():
    return mysql.connector.connect(
        host="localhost",  # e.g., "localhost"
        user="root",
        password="",
        database="clubsdb"
    )

# Function to fetch data and store in CSV
def fetch_and_store(table_name, filename):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)  # Dictionary cursor for column names

    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()

        if data:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data from {table_name} saved to {filename}")
        else:
            print(f"No data found in {table_name}")

    except mysql.connector.Error as e:
        print(f"Error fetching data from {table_name}: {e}")

    finally:
        cursor.close()
        conn.close()

# Tables to fetch
tables = {
    "club_ratings": "ratings.csv",
    "users": "users.csv",
    "clubs": "clubs.csv"
}

# Fetch and store each table
for table, file in tables.items():
    fetch_and_store(table, file)

import mysql.connector

# Create Database
conn = mysql.connector.connect(
    host="localhost",
    user="root",  # Change if your MySQL user is different
    password=""  # Replace with your actual MySQL password
)

cursor = conn.cursor()

# Create Database (if not exists)
cursor.execute("CREATE DATABASE IF NOT EXISTS club_recommendation")
cursor.execute("USE club_recommendation")

# Create Tables
tables = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            department VARCHAR(255),
            role ENUM('student', 'admin') DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "clubs": """
        CREATE TABLE IF NOT EXISTS clubs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT NOT NULL,
            category VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "memberships": """
        CREATE TABLE IF NOT EXISTS memberships (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            club_id INT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
        )
    """,
    "recommendations": """
        CREATE TABLE IF NOT EXISTS recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            club_id INT NOT NULL,
            recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
        )
    """,
    "notifications": """
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """,
    "events": """
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            club_id INT NOT NULL,
            event_name VARCHAR(255) NOT NULL,
            event_date DATETIME NOT NULL,
            description TEXT,
            FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
        )
    """
}

# Execute Table Creation
for table_name, table_query in tables.items():
    cursor.execute(table_query)

# Commit Changes
conn.commit()

print("Database and tables created successfully!")
import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",  # Replace with your actual password
        database="club_recommendation"
    )
    return conn


# Close Connection
cursor.close()
conn.close()

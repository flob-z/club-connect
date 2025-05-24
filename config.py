import os

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "club_recommendation"
}

SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")

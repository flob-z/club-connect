from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask_login import UserMixin
from sklearn.metrics.pairwise import cosine_similarity

db = SQLAlchemy()

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='user')  # user, club_leader, admin
    name = db.Column(db.String(100), nullable=False)

    # Relationship to track user-club interactions
    memberships = db.relationship('UserClub', backref='user', lazy=True)

# Club Model
class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional leader
    image = db.Column(db.String(255), nullable=True)  # Club logo
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    leader = db.relationship('User', backref='managed_club', foreign_keys=[leader_id])
    members = db.relationship('UserClub', backref='club', lazy=True)

# Many-to-Many Relationship: Users & Clubs
class UserClub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Event Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)  # Event poster
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    club = db.relationship('Club', backref=db.backref('events', lazy=True))
    organizer = db.relationship('User', backref=db.backref('organized_events', lazy=True))

# User-Club Recommendation System
def get_club_recommendations(user_id, num_recommendations=5):
    # Fetch user-club interaction data
    memberships = pd.read_sql_query(db.session.query(UserClub).statement, db.session.bind)

    if memberships.empty:
        return []

    user_club_matrix = memberships.pivot(index='user_id', columns='club_id', values='joined_at').fillna(0)
    user_similarity = cosine_similarity(user_club_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, index=user_club_matrix.index, columns=user_club_matrix.index)

    # Find similar users
    similar_users = user_similarity_df[user_id].sort_values(ascending=False).index[1:num_recommendations + 1]
    recommended_clubs = []

    for similar_user in similar_users:
        clubs_joined_by_similar_user = memberships[memberships['user_id'] == similar_user]
        recommended_clubs += list(clubs_joined_by_similar_user['club_id'])

    recommended_clubs = list(set(recommended_clubs))  # Remove duplicates
    return Club.query.filter(Club.id.in_(recommended_clubs)).all()[:num_recommendations]

# Initialize Database
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

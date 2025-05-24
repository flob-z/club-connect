import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session, flash ,g
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from db import get_db_connection  
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "clubsdb"

# Connect to MySQL
def connect_db():
    return MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)

# User Model
class User(UserMixin):
    def __init__(self, id, name, email, role=None):  # Added 'role' with a default value
        self.id = id
        self.name = name
        self.email = email
        self.role = role  # Store the role in the object


# Load User Function
@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(id=user['id'], name=user['name'], email=user['email'])
    return None

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        department = request.form['department']

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password, role, department) VALUES (%s, %s, %s, %s, %s)",
                           (name, email, password, role, department))
            conn.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()  # Remove leading/trailing spaces 
        password = request.form['password'].strip()

        conn = connect_db()
        cursor = conn.cursor()

        # Check in admin table
        cursor.execute('SELECT id, email, password, name, role FROM admin WHERE email = %s', (email,))
        admin = cursor.fetchone()

        if admin:
            stored_password = admin[2].strip()  # Ensure no extra spaces
            if stored_password == password:
                print("Admin login successful")
                user_obj = User(id=admin[0], name=admin[3], email=admin[1], role=admin[4])
                login_user(user_obj)
                session['user_id'] = user_obj.id
                session['user_name'] = user_obj.name
                session['role'] = user_obj.role
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))

        # Check in users table
        cursor.execute('SELECT id, email, password, name, role FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user[2].strip()
            if stored_password == password:
                print("User login successful")
                role = user[4].strip().lower()  # Normalize role
                user_obj = User(id=user[0], name=user[3], email=user[1], role=role)
                login_user(user_obj)
                session['user_id'] = user_obj.id
                session['user_name'] = user_obj.name
                session['role'] = user_obj.role
                flash('Login successful!', 'success')

                if role == 'student':
                    return redirect(url_for('dashboard'))
                elif role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash(f'Unrecognized role: {role}. Please contact support.', 'warning')
                    return redirect(url_for('login'))

        flash('Invalid email or password.', 'danger')
        conn.close()
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if 'user_id' not in session:
        flash('Session expired. Please log in again.', 'warning')
        return redirect(url_for('login'))

    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM notification WHERE user_id = %s AND is_read = 0", (session['user_id'],))
    unread_notifications_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html',
        name=session.get('user_name', 'User'),
        unread_notifications_count=unread_notifications_count
    )
@app.route('/clubs')
def list_clubs():
    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("""
        SELECT clubs.id, clubs.name, clubs.description, clubs.category, 
               clubs.image_url,  
               COALESCE(AVG(club_ratings.rating), 0) AS rating
        FROM clubs
        LEFT JOIN club_ratings ON clubs.id = club_ratings.club_id
        GROUP BY clubs.id
    """)
    
    clubs = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('clubs.html', clubs=clubs)


# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for('login'))

# Before Request Hook
@app.before_request
def before_request():
    if current_user.is_authenticated:
        conn = connect_db()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) AS unread_count FROM notifications WHERE user_id = %s AND is_read = 0", (current_user.id,))
        unread_count = cursor.fetchone()["unread_count"]
        cursor.close()
        conn.close()
        g.unread_notifications_count = unread_count
    else:
        g.unread_notifications_count = 0

# Context Processor to Inject Notifications
@app.context_processor
def inject_notifications():
    return {'unread_notifications_count': g.get('unread_notifications_count', 0)}


@app.route('/user_notifications')
@login_required
def user_notifications():
    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Fetch notifications for the logged-in user
    cursor.execute("SELECT * FROM notification WHERE user_id = %s ORDER BY created_at DESC", (current_user.id,))
    notifications = cursor.fetchall()

    # Mark all notifications as read for the user
    cursor.execute("UPDATE notification SET is_read = 1 WHERE user_id = %s", (current_user.id,))
    conn.commit()

    cursor.close()
    conn.close()

    return render_template('notifications.html', notifications=notifications)

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/faq')
def faq():
    return render_template('faq.html')
@app.route('/terms')
def terms():
    return render_template('terms.html')
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
@app.route('/update_profile', methods=['POST'])
def update_profile():
    pass  # Prevents IndentationError
@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Verify current password
    cursor.execute("SELECT password FROM users WHERE id=%s", (current_user.id,))
    user = cursor.fetchone()

    if user and user['password'] == current_password:  # Replace with proper hashing
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_password, current_user.id))
        conn.commit()
        flash("Password updated successfully!", "success")
    else:
        flash("Incorrect current password.", "danger")

    cursor.close()
    conn.close()

    return redirect(url_for('profile'))
from db import get_db_connection
from flask import Flask, request, jsonify
import pickle
import numpy as np
import pandas as pd
# Load the trained model & data
with open("model.pkl", "rb") as f:
    svd_model, scaler, student_club_matrix = pickle.load(f)

def recommend_clubs(student_id, top_n=3):
    """Generates club recommendations for a given student."""
    if student_id not in student_club_matrix.index:
        return ["No data for this student."]
    
    student_index = student_club_matrix.index.get_loc(student_id)
    
    # Transform student vector properly
    student_vector = scaler.transform(student_club_matrix.iloc[[student_index]])
    student_vector_svd = svd_model.transform(student_vector)

    # Compute similarity properly
    similarities = np.dot(student_vector_svd, svd_model.components_).flatten()

    # Get top N recommended clubs
    recommended_clubs = np.argsort(similarities)[::-1][:top_n]
    club_names = student_club_matrix.columns[recommended_clubs].tolist()
    
    return club_names

@app.route("/recommend", methods=["GET"])
@login_required
def get_recommendations():
    student_id = current_user.id  # Use the logged-in user's ID
    # student_id = request.args.get("student_id")
    if not student_id:
        return jsonify({"error": "Student ID is required!"}), 400
    
    recommendations = recommend_clubs(student_id)
    return jsonify({"student_id": student_id, "recommended_clubs": recommendations})

import MySQLdb

# Database connection
conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="clubsdb")
cursor = conn.cursor()

# Hash a sample password
hashed_password = generate_password_hash("admin123")  

# Insert admin user
# Connect to database
conn = connect_db()
cursor = conn.cursor()

# Check if the admin email already exists
cursor.execute("SELECT * FROM admin WHERE email = %s", ("admin@example.com",))
existing_admin = cursor.fetchone()

if not existing_admin:
    cursor.execute("INSERT INTO admin (name, email, password, role) VALUES (%s, %s, %s, %s)",
                   ("Admin", "admin@example.com", generate_password_hash("admin123"), "admin"))
    conn.commit()
    print("Admin account created successfully!")
else:
    print("Admin account already exists!")

cursor.close()
conn.close()


# Authentication Decorator
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash("You must be an admin to access this page.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch total users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    # Fetch total clubs
    cursor.execute("SELECT COUNT(*) FROM clubs")
    club_count = cursor.fetchone()[0]

    # Fetch total events
    cursor.execute("SELECT COUNT(*) FROM events")
    event_count = cursor.fetchone()[0]

    # Fetch unread messages count
    cursor.execute("SELECT COUNT(*) FROM messages WHERE status = 'unread'")
    unread_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'admin_dashboard.html',
        user_count=user_count,
        club_count=club_count,
        event_count=event_count,
        unread_count=unread_count
    )

@app.route('/events')
def events():
    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM events")  # Ensure the table exists and has data
    events = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('events.html', events=events)


@app.route('/manage_users')
@admin_required
def manage_users():
    conn = connect_db()  # Connect to the database
    cursor = conn.cursor()

    # Fetch all users
    cursor.execute("SELECT id, email, name, role, department FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template('manage_users.html', users=users)


@app.route('/manage_clubs')
@admin_required
def manage_clubs():
    conn = connect_db()
    cursor = conn.cursor()

    # Pagination Setup
    per_page = 10  # Number of clubs per page
    page = request.args.get('page', 1, type=int)  # Get page number from URL
    offset = (page - 1) * per_page

    # Fetch total club count
    cursor.execute("SELECT COUNT(*) FROM clubs")
    total_clubs = cursor.fetchone()[0]
    pages = (total_clubs // per_page) + (1 if total_clubs % per_page > 0 else 0)

    # Fetch paginated club records
    cursor.execute("SELECT id, name, description, category FROM clubs LIMIT %s OFFSET %s", (per_page, offset))
    clubs = cursor.fetchall()

    conn.close()

    return render_template('manage_clubs.html', clubs=clubs, pages=pages, current_page=page)


@app.route('/manage_events')
def manage_events():
    conn = connect_db()
    cursor = conn.cursor()

    sql = "SELECT id, name, description, date, location, created_at FROM events"
    cursor.execute(sql)
    events = cursor.fetchall()

    cursor.close()
    conn.close()

    # Convert tuples into dictionaries
    event_list = [
        {"id": e[0], "name": e[1], "description": e[2], "date": e[3], "location": e[4], "created_at": e[5]}
        for e in events
    ]

    return render_template('manage_events.html', events=event_list)

@app.route('/admin/notifications', methods=['GET', 'POST'])
@login_required
def admin_notifications():
    # Ensure only admin can access this page
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))  # Redirect non-admin users
    
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title'].strip()
        message = request.form['message'].strip()
        icon = request.form.get('icon', 'bell')  # Default icon if not provided

        if title and message:
            cursor.execute(
                "INSERT INTO notification (title, message, icon, created_at) VALUES (%s, %s, %s, NOW())",
                (title, message, icon)
            )
            conn.commit()
            flash('Notification created successfully!', 'success')
        else:
            flash('Title and message cannot be empty.', 'warning')

    # Fetch existing notifications
    cursor.execute("SELECT id, title, message, icon, created_at FROM notification ORDER BY created_at DESC")
    notifications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('notifications.html', notifications=notifications)

@app.route('/settings')
def settings():
    return render_template('settings.html')
@app.route('/admin_profile')
def admin_profile():
    return render_template('admin_profile.html')
@app.route('/change_password', methods=['POST'])
def change_password():
    # Your password change logic here
    return redirect(url_for('settings'))
@app.route('/update_account_settings', methods=['POST'])
def update_account_settings():
    # Your update logic here
    return redirect(url_for('settings'))
@app.route('/deactivate_account', methods=['POST'])
def deactivate_account():
    # Logic to deactivate the user's account
    return redirect(url_for('settings'))

@app.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        role = request.form['role']
        department = request.form['department']
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, name, role, department) VALUES (%s, %s, %s, %s)", 
            (email, name, role, department)
        )
        conn.commit()
        conn.close()

        flash('User added successfully!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('add_user.html')  # Create this template
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch user data
    cursor.execute("SELECT id, email, name, role, department FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('manage_users'))

    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        role = request.form['role']
        department = request.form['department']

        # Update user data
        cursor.execute(
            "UPDATE users SET email = %s, name = %s, role = %s, department = %s WHERE id = %s",
            (email, name, role, department, user_id)
        )
        conn.commit()
        conn.close()

        flash("User updated successfully!", "success")
        return redirect(url_for('manage_users'))

    conn.close()
    return render_template('edit_user.html', user=user)  # Make sure this template exists!
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    flash("User deleted successfully!", "success")
    return redirect(url_for('manage_users'))

@app.route('/new_club', methods=['GET', 'POST'])
@admin_required
def new_club():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clubs (name, description, category) VALUES (%s, %s, %s)", 
                       (name, description, category))
        conn.commit()
        conn.close()

        flash('Club added successfully!', 'success')
        return redirect(url_for('manage_clubs'))

    return render_template('new_club.html')


@app.route('/edit_club/<int:club_id>', methods=['GET', 'POST'])
def edit_club(club_id):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']

        sql = "UPDATE clubs SET name = %s, description = %s, category = %s WHERE id = %s"
        cursor.execute(sql, (name, description, category, club_id))
        conn.commit()

        flash("Club updated successfully!", "success")

        cursor.close()
        conn.close()
        return redirect(url_for('list_clubs'))  # Ensure 'list_clubs' exists

    # Fetch existing club details
    sql = "SELECT id, name, description, category FROM clubs WHERE id = %s"
    cursor.execute(sql, (club_id,))
    club = cursor.fetchone()

    cursor.close()
    conn.close()

    if club is None:
        flash("Club not found!", "danger")
        return redirect(url_for('list_clubs'))

    return render_template('edit_club.html', club={'id': club[0], 'name': club[1], 'description': club[2], 'category': club[3]})


@app.route('/delete_club/<int:club_id>', methods=['POST'])
def delete_club(club_id):
    conn = connect_db()
    cursor = conn.cursor()

    sql = "DELETE FROM clubs WHERE id = %s"
    cursor.execute(sql, (club_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Club deleted successfully!", "success")
    return redirect(url_for('list_clubs'))

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']

        conn = connect_db()
        cursor = conn.cursor()

        sql = "INSERT INTO events (name, description, date, location, created_at) VALUES (%s, %s, %s, %s, NOW())"
        cursor.execute(sql, (name, description, date, location))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Event added successfully!", "success")
        return redirect(url_for('manage_events'))  # Ensure this route exists

    return render_template('add_event.html')  # Ensure this template exists

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch the event by ID
    sql = "SELECT id, name, description, date, location FROM events WHERE id = %s"
    cursor.execute(sql, (event_id,))
    event = cursor.fetchone()

    if not event:
        flash("Event not found!", "danger")
        return redirect(url_for('manage_events'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']

        sql_update = "UPDATE events SET name = %s, description = %s, date = %s, location = %s WHERE id = %s"
        cursor.execute(sql_update, (name, description, date, location, event_id))
        conn.commit()

        flash("Event updated successfully!", "success")
        return redirect(url_for('manage_events'))

    cursor.close()
    conn.close()

    return render_template('edit_event.html', event={
        "id": event[0], "name": event[1], "description": event[2], "date": event[3], "location": event[4]
    })

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    conn = connect_db()
    cursor = conn.cursor()

    sql = "DELETE FROM events WHERE id = %s"
    cursor.execute(sql, (event_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Event deleted successfully!", "success")
    return redirect(url_for('manage_events'))


@app.route('/reports', methods=['GET'])
def reports():
    conn = connect_db()
    if conn is None:
        return "Error: Unable to connect to the database", 500

    cursor = conn.cursor()

    # Total counts
    cursor.execute("SELECT COUNT(*) FROM clubs")
    total_clubs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    # Role-based user count
    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    users_per_role = cursor.fetchall()  # [(role, count), ...]

    # Top-rated clubs (assuming ratings exist)
    cursor.execute("""
        SELECT club_id, AVG(rating) AS avg_rating 
        FROM club_reviews 
        GROUP BY club_id 
        ORDER BY avg_rating DESC 
        LIMIT 5
    """)
    top_rated_clubs = cursor.fetchall()  # [(club_id, avg_rating), ...]

    # Most active clubs (by membership count)
    cursor.execute("""
        SELECT club_id, COUNT(*) AS member_count 
        FROM memberships 
        GROUP BY club_id 
        ORDER BY member_count DESC 
        LIMIT 5
    """)
    most_active_clubs = cursor.fetchall()  # [(club_id, member_count), ...]

    # Most participated events
    cursor.execute("""
        SELECT event_id, COUNT(*) AS participant_count 
        FROM event_participants 
        GROUP BY event_id 
        ORDER BY participant_count DESC 
        LIMIT 5
    """)
    most_participated_events = cursor.fetchall()  # [(event_id, participant_count), ...]

    # Rating distribution for clubs
    cursor.execute("""
        SELECT rating, COUNT(*) AS count 
        FROM club_reviews 
        GROUP BY rating 
        ORDER BY rating
    """)
    rating_distribution = cursor.fetchall()  # [(rating, count), ...]

    # Active users (based on event participation)
    cursor.execute("""
        SELECT user_id, COUNT(*) AS participation_count 
        FROM event_participants 
        GROUP BY user_id 
        ORDER BY participation_count DESC 
        LIMIT 5
    """)
    active_users = cursor.fetchall()  # [(user_id, participation_count), ...]

    cursor.close()
    conn.close()

    return render_template(
        'report.html',
        total_clubs=total_clubs,
        total_users=total_users,
        total_events=total_events,
        users_per_role=users_per_role,
        top_rated_clubs=top_rated_clubs,
        most_active_clubs=most_active_clubs,
        most_participated_events=most_participated_events,
        rating_distribution=rating_distribution,
        active_users=active_users
    )

@app.route('/club/<int:club_id>')
def club_detail(club_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM clubs WHERE id = %s", (club_id,))
    club = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    
    return render_template('club_detail.html', club=club)

from flask import Flask, render_template, request
import logging
import pickle
import numpy as np
from flask_login import login_required

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Load data with error handling
try:
    popular_df = pickle.load(open('popular.pkl', 'rb'))
    pt = pickle.load(open('pt.pkl', 'rb'))
    clubs = pickle.load(open('clubs.pkl', 'rb'))
    similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))
    logging.info("Pickle files loaded successfully.")
except Exception as e:
    logging.error(f"Error loading pickle files: {e}")
    popular_df = pt = clubs = similarity_scores = None

@app.route('/index')
@login_required
def index():
    try:
        if popular_df is not None:
            return render_template('index.html',
                                   club_name=list(popular_df['name'].values),
                                   category=list(popular_df['category'].values),
                                   image=list(popular_df['image_url'].values),
                                   votes=list(popular_df['num_ratings'].values),
                                   rating=list(popular_df['avg_rating'].values)
                                   )
        else:
            logging.error("Popular dataframe is None.")
            return "Error loading popular clubs data", 500
    except Exception as e:
        logging.error(f"Error rendering index: {e}")
        return "An error occurred while processing your request", 500

@app.route('/recommend')
@login_required
def recommend_clubs():
    return render_template('recommend.html')

@app.route('/recommend', methods=['GET', 'POST'])
@login_required
def recommend():
    try:
        user_input = request.form.get('user_input')

        # Normalize the user input and club names for consistent matching

        # Check if user_input is valid
        if user_input not in [name.lower() for name in clubs['name'].values]:
            logging.warning(f"Invalid user input: {user_input}")
            return render_template('recommend.html', data=[], message="Club not found in the dataset.")

        # Get the corresponding club ID from the dataset
        club_id = clubs[clubs['name'].str.lower() == user_input]['club_id'].values[0]

        # Check if the club is present in the pivot table
        if club_id not in pt.index:
            logging.warning(f"Club ID {club_id} not found in the pivot table.")
            return render_template('recommend.html', data=[], message="Club not found in the pivot table.")

        index = list(pt.index).index(club_id)

        # Get similar items using cosine similarity
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

        data = []
        for i in similar_items:
            item = []
            temp_df = clubs[clubs['club_id'] == pt.index[i[0]]]

            # Extract club details, avoiding duplicates
            item.extend(temp_df['name'].drop_duplicates().values.tolist())
            item.extend(temp_df['category'].drop_duplicates().values.tolist())
            item.extend(temp_df['image_url'].drop_duplicates().values.tolist())

            # Ensure item contains expected values
            data.append(item)

        logging.info(f"Recommendation data: {data}")
        return render_template('recommend.html', data=data)

    except Exception as e:
        logging.error(f"Error during recommendation: {e}")
        return render_template('recommend.html', data=[], message="An error occurred while processing your request.")
@app.route('/clubs')
def clubs():
    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    
    search_query = request.args.get('search', '')

    if search_query:
        cursor.execute("SELECT * FROM clubs WHERE name LIKE %s OR category LIKE %s", 
                       ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute("SELECT * FROM clubs")

    clubs = cursor.fetchall()

    # Fetch ratings for each club
    for club in clubs:
        cursor.execute("SELECT AVG(rating) as avg_rating FROM club_ratings WHERE club_id = %s", (club['id'],))
        result = cursor.fetchone()
        club['rating'] = round(result['avg_rating'], 1) if result['avg_rating'] else 0  # Round to 1 decimal place

    cursor.close()
    conn.close()

    return render_template('clubs.html', clubs=clubs)

@app.route('/rate_club/<int:club_id>', methods=['POST'])
def rate_club(club_id):
    if 'user_id' not in session:
        if request.is_json:  # Check if it's an AJAX request
            return jsonify({"error": "You need to log in to rate a club."}), 401
        else:
            flash("You need to log in to rate a club.", "danger")
            return redirect(url_for('login'))

    user_id = session['user_id']  # Get user ID from session
    
    # Handle both JSON (AJAX) and form requests
    if request.is_json:
        data = request.get_json()
        rating = data.get("rating")
    else:
        rating = request.form.get("rating")

    if not rating:
        if request.is_json:
            return jsonify({"error": "Please provide a rating."}), 400
        else:
            flash("Please select a rating before submitting.", "warning")
            return redirect(url_for('club_details', club_id=club_id))

    conn = connect_db()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    # Check if user already rated this club
    cursor.execute("SELECT * FROM club_ratings WHERE user_id = %s AND club_id = %s", (user_id, club_id))
    existing_rating = cursor.fetchone()

    if existing_rating:
        cursor.execute("UPDATE club_ratings SET rating = %s WHERE user_id = %s AND club_id = %s", 
                       (rating, user_id, club_id))
    else:
        cursor.execute("INSERT INTO club_ratings (user_id, club_id, rating) VALUES (%s, %s, %s)", 
                       (user_id, club_id, rating))

    conn.commit()

    # Calculate the new average rating
    cursor.execute("SELECT AVG(rating) as avg_rating FROM club_ratings WHERE club_id = %s", (club_id,))
    avg_rating = cursor.fetchone()["avg_rating"]

    cursor.close()
    conn.close()

    if request.is_json:
        return jsonify({"message": "Rating submitted successfully!", "new_rating": avg_rating})

    flash("Your rating has been submitted!", "success")
    return redirect(url_for('club_details', club_id=club_id))

@app.route('/join_club/<int:club_id>', methods=['POST'])
def join_club(club_id):
    # Logic to add user to the club
    return redirect(url_for('club_detail', club_id=club_id))
# Toggle Favorite Club
@app.route('/toggle_favorite_club/<int:club_id>', methods=['POST'])
def toggle_favorite_club(club_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Check if club is already a favorite
    cursor.execute("SELECT is_favorite FROM clubs WHERE id = %s", (club_id,))
    club = cursor.fetchone()

    if club:
        new_status = 0 if club[0] else 1  # Toggle between 0 and 1
        cursor.execute("UPDATE clubs SET is_favorite = %s WHERE id = %s", (new_status, club_id))
        conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('clubs'))


if __name__ == '__main__':
    app.run(debug=True)
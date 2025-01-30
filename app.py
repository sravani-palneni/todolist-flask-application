# Import necessary libraries and modules
from flask import Flask, request, redirect, url_for, flash
from model import db, TaskDetails, UserDetails
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime, timedelta
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create the Flask application
app = Flask(__name__)

# Set the secret key for the application (used for session management)
app.secret_key = os.getenv('SECRET_KEY')

# Initialize the LoginManager for user authentication
login_manager = LoginManager()
login_manager.init_app(app)

# Set the login view (page where users are redirected if they are not logged in)
login_manager.login_view = "userLogin"

# User Loader function for Flask-Login (retrieves user from the database based on user_id)
@login_manager.user_loader
def load_user(user_id):
    return UserDetails.query.get(int(user_id))

# Set Twilio credentials and Initialize the Twilio client (Used for sending SMS notifications to users)
twilio_sid = os.getenv("TWILIO_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number  = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(twilio_sid, twilio_auth_token)

# Set APScheduler (for scheduling reminders for due tasks)
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

# SQLALCHEMY_DATABASE_URI: The database URI to specify the database you want to establish a connection with.
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")	

 # A configuration to enable or disable tracking modifications of objects.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False	

# Initialize the SQLAlchemy instance with the app
db.init_app(app)

# Before each request, ensure that all database tables are created 
@app.before_request
def create_table():
    db.create_all()

# Route for the Index Page of the application
@app.route('/')
def index():		
    return render_template('index.html')	

# Route for the User's Home Page
@app.route('/home')
@login_required  #Ensures that only logged in users can access this page
def home():		   
    tasks = TaskDetails.query.filter_by(user_id=current_user.user_id)
    return render_template('showtasklist.html', tasks=tasks)	

# Route to add a new task (only for logged-in users)
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'GET':
        return render_template('addtask.html')
    if request.method == 'POST':	
        title = request.form['title']						
        category = request.form['category']
        priority = request.form['priority']
        due_date = request.form['duedate']
        user_id=current_user.user_id
        task = TaskDetails (title=title, category=category, priority=priority, due_date=due_date, user_id=user_id)
        
        # Add the task to the database and commit the changes
        db.session.add(task)
        db.session.commit()
        #flash("Task added Successfully.", "success")
        return redirect(f'/home')    # Redirect to the homepage to display updated tasks

# Route to search for a specific task (only for logged-in users)
@app.route('/tasks/search', methods=['GET', 'POST'])
@login_required
def search_tasks():
    if request.method == 'POST':
        search_term = request.form['search-term']
        if search_term:
            tasks = TaskDetails.query.filter(
                TaskDetails.title.ilike(f'%{search_term}%'),  TaskDetails.user_id == current_user.user_id).all()
        else:
            tasks = TaskDetails.query.filter_by(user_id=current_user.user_id).all()
        return render_template('showtasklist.html', tasks=tasks)
    

# Route to delete a task by its ID (only for logged-in users)
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    task = TaskDetails.query.filter_by(task_id=id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return redirect(f'/home')

# Route to update the task status as complete (only for logged-in users)
@app.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    task = TaskDetails.query.filter_by(task_id=id).first()
    task.status = True
    db.session.commit()
    return redirect(f'/home')

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def registerUser():
    if request.method == 'GET':
        return render_template('registeruser.html') 
    if request.method == 'POST':	
        full_name = request.form['fullname']						
        email_id = request.form['emailid']
        mobile_no = request.form['mobileno']
        password= request.form['password']

        # Check if all fields are filled out
        if not full_name or not email_id or not mobile_no or not password:
            flash("Please fill in all fields.", 'danger')
            return render_template('registeruser.html')

        # Check if the username already exists
        existing_user = UserDetails.query.filter_by(email_id=email_id).first()
        if existing_user:
            flash('Email already exists, Please use a different one.', 'danger')
            return render_template('registeruser.html')  

        # Hashing the password before saving it
        hashed_password = generate_password_hash(password)

        user = UserDetails (full_name=full_name, email_id=email_id, mobile_no=mobile_no, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Registration successful! Please log in.", category="success")
        return redirect("/login")

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def userLogin():
    # Redirect to homepage if already logged in 
    if current_user.is_authenticated:
        return redirect(f'/home')
    
    if request.method == 'GET':
        return render_template('userlogin.html') 
    if request.method == 'POST':	
        username = request.form['username']						
        password= request.form['password']

        if not username or not password:
            flash("Please enter both username and password.", 'danger')
            return redirect("/login")

        user = UserDetails.query.filter_by(email_id=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(f'/home')
            flash("Login failed. Check your username and/or password.", "danger")
            return redirect("/")
        flash("Username does not exist", "danger")
        return redirect("/")

# Route to display user profile (only for logged-in users)  
@app.route('/profile')
@login_required
def userProfile():
    user = UserDetails.query.filter_by(user_id=current_user.user_id).first()
    return render_template('userprofile.html', user=user)

# Route to update user profile (only for logged-in users)
@app.route('/profile/update/', methods=['GET', 'POST'])
@login_required
def profileUpdate():
    user = UserDetails.query.filter_by(user_id=current_user.user_id).first()
    if user:
        if request.method == 'GET':
            return render_template('updateprofile.html', user=user)
        if request.method == 'POST':
            full_name = request.form['fullname']
            email_id = request.form['emailid']
            mobile_no = request.form['mobileno']
            
            user.full_name = full_name
            user.email_id = email_id
            user.mobile_no = mobile_no
            
            db.session.commit()
            flash("Details Updated Successfully", "success")
            return redirect(f'/profile')
        
# Route for user logout
@app.route('/logout')
def userLogout():
    logout_user()
    flash("Successfully Logout", "success")
    return redirect("/")


# Function to calculate due tasks and send SMS reminders (runs daily)
def calculateDueDate():
    # Getting tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = tomorrow.date()  #Extrating just the date part 

    tasks_due_tomorrow = TaskDetails.query.filter_by(due_date = tomorrow).all()


    for task in tasks_due_tomorrow:
        user = UserDetails.query.filter_by(user_id = task.user_id).first()
        if user:
            message_body = f"Reminder: Your task '{task.title}' is due tomorrow ({task.due_date})."
            send_sms(user.mobile_no, message_body) 

# Function to send SMS using Twilio
def send_sms(to_mobile, message):
    message = client.messages.create(body=message, from_=twilio_phone_number, to='+61'+to_mobile)

# Add the `calculateDueDate` function to the scheduler to run daily at 11:00 PM
scheduler.add_job(func=calculateDueDate, trigger="cron", hour=23, minute=0)

# Run the Flask app
if __name__=='__main__':
	app.run()			
			
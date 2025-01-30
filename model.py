from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class TaskDetails(db.Model):          
    __tablename__ = "task_table"

    task_id = db.Column(db.Integer(), primary_key = True)
    title = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=True)  # Personal, Study, Work, Food, Payments
    priority = db.Column(db.String(50), nullable=False)  # Low, Medium, High
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_table.user_id'), nullable=False)

    user = db.relationship('UserDetails', backref='tasks')  

    def __repr__(self):
        return f'<Task {self.title}>'

class UserDetails(db.Model, UserMixin):          
    __tablename__ = "user_table"

    user_id = db.Column(db.Integer(), primary_key = True)
    full_name = db.Column(db.String(50), nullable=False)
    email_id = db.Column(db.String(50), unique=True)  
    mobile_no = db.Column(db.String(20), nullable=False)  
    password = db.Column(db.String(500), nullable=False)

    def get_id(self):
        return self.user_id
    

    
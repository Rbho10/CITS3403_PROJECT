from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"
    

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Subjects(db.Model):
    __tablename__ = 'studySubjects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    subject_name = db.Column(db.String(30), unique=True, nullable=False)
    graph_type = db.Column(db.String(20), nullable=False)
    graph_scale = db.Column(db.Integer, nullable=False)
    privacy = db.Column(db.String(20), nullable=False)
    opinion_toggle = db.Column(db.Boolean, default=True, nullable=False)
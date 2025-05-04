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

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('subjects', lazy=True))

    def __repr__(self):
        return f"<Subject {self.id}: {self.name}>"
    
class LogSession(db.Model):
    __tablename__ = 'logsessions'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    study_duration = db.Column(db.Integer)  # in minutes
    break_time = db.Column(db.Integer, default=0)
    mood_level = db.Column(db.Integer)
    study_environment = db.Column(db.String(50))
    mental_load = db.Column(db.Integer)
    distractions = db.Column(db.String(255))
    goal_progress = db.Column(db.String(20))
    focus_level = db.Column(db.Integer)
    effectiveness = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    subject = db.relationship('Subject', backref=db.backref('logsessions', lazy=True))
    user = db.relationship('User', backref=db.backref('logsessions', lazy=True))

    def __repr__(self):
        return f"<LogSession {self.id} for Subject {self.subject_id} by User {self.user_id}>"
class SharedSubject(db.Model):
    __tablename__ = 'shared_subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    subject = db.relationship('Subject', backref='shared_with')
    shared_with_user = db.relationship('User', foreign_keys=[shared_with_user_id], backref='shared_subjects_received')
    shared_by_user = db.relationship('User', foreign_keys=[shared_by_user_id], backref='shared_subjects_sent')

    def __repr__(self):
        return f"<SharedSubject: Subject {self.subject_id} shared from User {self.shared_by_user_id} to User {self.shared_with_user_id}>"

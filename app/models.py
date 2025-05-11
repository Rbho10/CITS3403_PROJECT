from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()
from werkzeug.security import generate_password_hash, check_password_hash
# import werkzeug.security so we can use it to hash passwords when updating

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    profile_picture = db.Column(db.String(255), nullable=True)

    
    

    api_responses = db.relationship('ApiResponse', back_populates='user', lazy='dynamic')

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"
    def set_password(self, raw_password):
        """Hash and store a new password."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password, raw_password)
    

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Subject(db.Model):
    __tablename__ = 'subjects'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='uq_user_subject'),
    )

    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('subjects', lazy=True))
    api_responses = db.relationship('ApiResponse', back_populates='subject', lazy='dynamic')

    def __repr__(self):
        return f"<Subject {self.id}: {self.name}>"

    
class SharedSubject(db.Model):
    __tablename__ = 'shared_subjects'
    __table_args__ = (
        db.UniqueConstraint(
            'subject_id',
            'owner_id',
            'shared_with_user_id',
            name='uq_shared_subject'
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    

    subject = db.relationship('Subject', backref='shared_with')
    owner = db.relationship('User', foreign_keys=[owner_id], backref="owner_of_subjects")
    shared_with_user = db.relationship('User', foreign_keys=[shared_with_user_id], backref="shared_subjects")

    def __repr__(self):
        return f"<SharedSubject: Subject {self.subject_id} shared with User {self.shared_with_user_id} from User {self.owner_id}>"
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
    
class ApiResponse(db.Model):
    __tablename__ = 'api_responses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    # store the full JSON payload
    # - on SQLite this ends up as TEXT but you can still load/dump with json
    # - if your DB supports native JSON you can use db.JSON
    response_data = db.Column(db.JSON, nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # optional back-refs
    user = db.relationship('User', back_populates='api_responses')
    subject = db.relationship('Subject', back_populates='api_responses')
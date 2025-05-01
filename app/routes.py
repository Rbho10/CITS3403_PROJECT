from flask import render_template, redirect, url_for, flash
from app import app
from flask import request, jsonify, session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user
from app.models import db, User, Friendship, Subject, LogSession
from app.signup_form import SignUpForm

@app.route('/')
def welcome():
    return render_template('welcomePage.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))  
        else:
            flash("Invalid username or password.", "danger")

    return render_template("loginPage.html")

@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('welcome'))

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignUpForm()

    if request.method == "POST" and form.validate_on_submit():
        first_name = request.form['first_name']
        last_name = request.form.get('last_name', '')
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']


       # Check for duplicates
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return render_template("signup.html", form=form)

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("signup.html", form=form)

        # Hash and save
        hashed_password = generate_password_hash(password)
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("accountcreationpage.html", form=form)

@app.route('/users')
def show_users():
    users = User.query.all()
    return "<br>".join([f"{u.id}: {u.username} - {u.email} - {u.first_name} - {u.created_at}" for u in users])

@app.route('/friends')
def friends():
    return render_template("friends.html")

@app.route('/search_friends')
def search_friends():
    query = request.args.get('query', '')

    user_id = current_user.id

    if query:
        users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    else:
        users = User.query.all()

    results = []

    for user in users:
        if user_id is not None and user.id == user_id:
            continue  # skip yourself

        # Default to not a friend
        is_friend = False

        if user_id:
            # Check if friendship exists (in either direction)
            friendship = Friendship.query.filter(
                ((Friendship.user_id == user_id) & (Friendship.friend_id == user.id)) |
                ((Friendship.user_id == user.id) & (Friendship.friend_id == user_id))
            ).first()

            if friendship:
                is_friend = True

        results.append({
            'id': user.id,
            'username': user.username,
            'meta': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else "",
            'is_friend': is_friend
        })

    return jsonify(friends=results)


@app.route('/add_friend', methods=['POST'])
def add_friend():
    data = request.get_json()
    friend_id = data['friend_id']
    user_id = current_user.id

    existing = Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    if not existing:
        friendship = Friendship(user_id=user_id, friend_id=friend_id)
        db.session.add(friendship)
        db.session.commit()
        return '', 200
    else:
        return '', 400
    
@app.route('/add_subject', methods=["POST"])
def add_subject():
    subject_name = request.form.get('name')
    new_subject = Subject(name=subject_name, user_id=current_user.id)
    db.session.add(new_subject)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_logsession', methods=["POST"])
def add_logsession():
    data = request.form
    new_log = LogSession(
        description=data.get('description'),
        study_duration=int(data.get('study_duration')),
        break_time=int(data.get('break_time', 0)),
        mood_level=int(data.get('mood_level')),
        study_environment=data.get('study_environment'),
        mental_load=int(data.get('mental_load')),
        distractions=data.get('distractions', ''),
        goal_progress=data.get('goal_progress'),
        focus_level=int(data.get('focus_level')),
        effectiveness=int(data.get('effectiveness')),
        subject_id=int(data.get('subject_id'))
    )
    db.session.add(new_log)
    db.session.commit()
    return redirect(url_for('dashboard'))


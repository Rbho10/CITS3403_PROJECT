from flask import render_template, redirect, url_for, flash
from app import app
from flask import request, jsonify, session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user
from app.models import db, User, Friendship, Subjects, Sessions
from app.signup_form import SignUpForm
from app.createStudySubject_form import CreateStudySubjectForm
from app.createSessionForm import CreateSessionForm
from app.models import db, User, Friendship
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

@app.route('/subjects')
def subjects():
    return render_template("mySubjectsPage.html")

@app.route('/search_subjects')
def search_subjects():
    query = request.args.get('query', '')
    user_id = current_user.id

    if query:
        subjects = Subjects.query.filter(Subjects.subject_name.ilike(f"%{query}%")).all()
    else:
        subjects = Subjects.query.all()
    
    results = []

    for subject in subjects:
        if user_id is not None and subject.user_id != user_id:
            continue

        results.append({
            'id': subject.id,
            'subject_name': subject.subject_name
        })
    
    return jsonify(studysubject=results)

@app.route('/create_subject', methods=["POST","GET"])
def createSubject():
    form = CreateStudySubjectForm()
    user_id = current_user.id

    if request.method == "POST" and form.validate_on_submit():
        subject_name = request.form["subject_name"]
        #graph_type = request.form["graph_type"]
        #graph_scale = request.form["graph_scale"]
        #privacy = request.form["privacy"]
        #opinion_toggle = request.form["opinion_toggle"]

        #check for duplicate subject names
        if Subjects.query.filter_by(subject_name=subject_name, user_id=user_id).first():
            flash("Subject already exists.", "danger")
            return render_template("createStudySubject.html", form=form)

        #create new subject
        new_subject = Subjects(
            user_id=user_id,
            subject_name=subject_name,
            #graph_type=graph_type,
            #graph_scale=graph_scale,
            #privacy=privacy,
            #opinion_toggle=opinion_toggle
        )
        db.session.add(new_subject)
        db.session.commit()

        flash("New subject created.", "success")
        return redirect(url_for("subjects"))

    return render_template("createStudySubject.html", form=form)

@app.route('/subject/<int:id>/<string:subject_name>', methods=["POST","GET"])
def loadInsight(id, subject_name):
    id = 1
    subject_name = "German"
    return render_template("subject.html", id=id, subject_name=subject_name)

@app.route('/subject/<int:URLid>/<string:URLsubject_name>/addSession', methods=["POST","GET"])
def addSession(URLid, URLsubject_name):
    URLid = URLid
    URLsubject_name = URLsubject_name
    user_id = current_user.id

    form = CreateSessionForm()

    if request.method == "POST" and form.validate_on_submit():
        date = request.form["date"]
        study_duration = request.form["study_duration"]
        study_break = request.form["study_break"]
        energy_level_before = request.form["energy_level_before"]
        energy_level_after = request.form["energy_level_after"]
        difficulty = request.form["difficult"]
        environment = request.form["environment"]
        progress = request.form["progress"]
        
        new_log = Sessions( 
            user_id = user_id,
            subject_name = URLsubject_name,
            subject_id = URLid,
            date=date,
            study_duration=study_duration,
            study_break=study_break,
            energy_level_before=energy_level_before,
            energy_level_after=energy_level_after,
            difficulty=difficulty,
            environment=environment,
            progress=progress
        )
        db.session.add(new_log)
        db.session.commit()

        flash("New session created.", "success")
        return redirect(url_for("subjects"))

    return render_template("addSession.html", form=form, id=URLid, subject_name=URLsubject_name)
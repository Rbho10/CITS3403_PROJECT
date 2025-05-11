import os
import openai
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user, login_user, logout_user
from app.generate_insights import generate_insights_core
from app import app
from flask import request, jsonify, session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from app.models import db, User, Friendship, Subject, SharedSubject, LogSession
from werkzeug.utils import secure_filename


from app.signup_form import SignUpForm, LogSessionForm, SettingsForm, LoginForm


from app.generate_insights import generate_insights_core, _build_insight_data

@app.route('/')
def welcome():
    return render_template('welcomePage.html')

@app.route('/time-tracker')
def time_tracker():
    return render_template('timeTracker.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # use your model’s check_password method
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        # invalid credentials fallback
        flash("Invalid username or password.", "danger")
    # on GET, or after a failed POST, just render the form (with any flash messages)
    return render_template("loginPage.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('welcome'))

@app.route('/dashboard')
@login_required
def dashboard():
    # —— OWNED SUBJECTS ——
    raw = current_user.subjects
    seen = set()
    owned = []
    for s in raw:
        if s.name not in seen:
            seen.add(s.name)
            owned.append(s)

    insights_owned = {
        s.id: _build_insight_data(current_user.id, s.name)
        for s in owned
    }
    # —— SUBJECTS SHARED WITH ME ——
    shares = SharedSubject.query.filter_by(shared_with_user_id=current_user.id).all()
    seen_shared = set()
    shared = []
    for sh in shares:
        key = (sh.owner_id, sh.subject.name)
        if key not in seen_shared:
            seen_shared.add(key)
            shared.append(sh)

    insights_shared = {
        sh.subject.id: _build_insight_data(sh.owner_id, sh.subject.name)
        for sh in shared
    }

    # —— USERS I CAN SHARE TO ——
    share_users = User.query.filter(User.id != current_user.id).all()

    return render_template(
        'dashboard.html',
        subjects=owned,
        insights=insights_owned,
        shared=shared,
        insights_shared=insights_shared,
        share_users=share_users
    
    )
@app.route('/share_subject', methods=['POST'])
@login_required
def share_subject():
    data = request.get_json() or {}
    subject_id     = data.get('subject_id')
    target_user_id = data.get('target_user_id')

    if not subject_id or not target_user_id:
        return jsonify(status='error', message='Missing parameters'), 400

    subj = Subject.query.filter_by(
        id=subject_id, user_id=current_user.id
    ).first_or_404()

    exists = SharedSubject.query.filter_by(
        subject_id=subj.id,
        owner_id=current_user.id,
        shared_with_user_id=target_user_id
    ).first()
    if exists:
        return jsonify(status='exists')

    share = SharedSubject(
        subject_id=subj.id,
        owner_id=current_user.id,
        shared_with_user_id=target_user_id
    )
    db.session.add(share)
    db.session.commit()
    return jsonify(status='ok')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists.", "danger")
            return render_template("accountcreationpage.html", form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return render_template("accountcreationpage.html", form=form)

        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data or '',
            email=form.email.data,
            username=form.username.data
        )
        new_user.set_password(form.password.data)
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
        return '', 

@app.route('/insights/<int:user_id>/<path:subject>')
@login_required
def insights(user_id, subject):
    # 1) permission: only yourself (or add sharing logic here)
    if user_id != current_user.id:
        abort(403)

    # 2) hand off to the core generator
    return generate_insights_core(user_id, subject)

@app.route('/subjects')
def subjects():
    return render_template("mySubject.html")

@app.route('/search_subjects')
@login_required
def search_subjects():
    query = request.args.get('query', '').strip()
    user_id = current_user.id

    # Base query: only this user’s subjects
    subjects_q = Subject.query.filter_by(user_id=user_id)

    # If there’s a search term, add an ILIKE filter
    if query:
        subjects_q = subjects_q.filter(Subject.name.ilike(f"%{query}%"))

    subjects = subjects_q.all()

    # Serialize to JSON
    results = [
        {"id": s.id, "name": s.name}
        for s in subjects
    ]

    return jsonify(subjects=results)

@app.route('/create_subject', methods=['GET','POST'])
@login_required
def create_subject():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Please enter a subject name.', 'danger')
            return redirect(url_for('create_subject'))

        # 1) create new Subject row
        subj = Subject(name=name, user_id=current_user.id)
        db.session.add(subj)
        db.session.commit()

        # 2) send user to the “add session” form for this new subject
        return redirect(url_for('add_session', subject_id=subj.id))

    # GET → show the plain form
    return render_template('createSubject.html')

@app.route('/subject/<int:subject_id>/add_session', methods=['GET', 'POST'])
@login_required
def add_session(subject_id):
    # Ensure the subject exists and belongs to the current user
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()

    form = LogSessionForm()
    if form.validate_on_submit():
        log = LogSession(
            description      = form.description.data,
            study_duration   = form.study_duration.data,
            break_time       = form.break_time.data or 0,
            mood_level       = form.mood_level.data,
            study_environment= form.study_environment.data,
            mental_load      = form.mental_load.data,
            distractions     = form.distractions.data,
            goal_progress    = form.goal_progress.data,
            focus_level      = form.focus_level.data,
            effectiveness    = form.effectiveness.data,
            subject_id       = subject.id,
            user_id          = current_user.id
        )
        db.session.add(log)
        db.session.commit()

        flash('Study session added successfully.', 'success')
        return redirect(url_for('view_subject', subject_id=subject.id))

    return render_template(
        'addSession.html',
        form=form,
        subject=subject
    )

@app.route('/subject/<int:subject_id>')
@login_required
def view_subject(subject_id):
    # load the subject, or 404 if it doesn’t exist / isn’t yours
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first()
    if subject is None:
        abort(404)

    # you can pass its log‐sessions through the relationship
    sessions = subject.logsessions  # list of LogSession objects

    return render_template(
        'viewSubject.html',
        subject=subject,
        sessions=sessions
    )



@app.route('/profile-page', methods=['GET', 'POST'])
@login_required
def profile_page():
    form = SettingsForm()

    if form.validate_on_submit():
        if form.new_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('Incorrect current password. Password not updated.', 'danger')
                return redirect(url_for('profile_page'))
            current_user.set_password(form.new_password.data)

        if form.username.data and form.username.data != current_user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already taken.', 'danger')
                return redirect(url_for('profile_page'))
            current_user.username = form.username.data
        if form.email.data and form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered.', 'danger')
                return redirect(url_for('profile_page'))
            current_user.email = form.email.data
        
        current_user.first_name = form.first_name.data or current_user.first_name
        current_user.last_name  = form.last_name.data  or current_user.last_name
        file = form.profile_picture.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"user_{current_user.id}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print("Saving file to:", filepath)  
            file.save(filepath)
            current_user.profile_picture = f"uploads/{filename}"

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile_page'))

    return render_template('profile-page.html', form=form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

from flask import render_template, redirect, url_for, flash
from app import app
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user
from app.models import db, User
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

   #find all users whose username contains the query text, case-insensitive.
    friends = User.query.filter(User.username.ilike(f"%{query}%")).all()

    # Format results
    results = []
    for friend in friends:
        results.append({
            'username': friend.username,
        })

    return jsonify({'friends': results})
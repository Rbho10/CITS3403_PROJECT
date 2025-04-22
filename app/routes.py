from flask import render_template
from app import app
from flask import request, redirect, url_for, jsonify

@app.route('/')
def welcome():
    return render_template('welcomePage.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template("logInPage.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/AccountsCreation', methods=["GET", "POST"])
def signup():
    return render_template("accountcreationpage.html")

from flask import Blueprint, redirect, render_template, request, flash
from flask_login import login_user, login_required, logout_user, current_user
import hashlib
from . import mysql
from .queries import getUser, insertUser
from .models import User

auth = Blueprint('auth', __name__)

#fix bug - user can log into another account even if in an account

@auth.route('/')
def default():
    return redirect('/login')

@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        username = request.form.get("username")
        password = request.form.get("password")

        existingUser = getUser(username)

        if existingUser:    
            flash("Username already exists", category="error")
        elif len(firstName) > 25:
            flash("First name must be 25 characters or less.", category="error")
        elif len(lastName) > 25:
            flash("Last name must be 25 characters or less.", category="error")
        elif len(username) > 15:
            flash("Username must be 15 characters or less.", category="error")
        elif len(password) > 50:
            flash("Password must be 50 characters or less.", category="error")
        else:
            insertUser(username, password, firstName, lastName, 'test')
            newUser = getUser(username)

            if newUser:
                objUser = User(*newUser)
                login_user(objUser)
                flash("Account created!", category="success")
                return redirect('/dashboard')
            else:
                flash("Error creating account.", category="error")

    return render_template("signup.html")
    

@auth.route('/login', methods=['GET', 'POST'])
def login():    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        loginHashedPassword = hashlib.sha256(password.encode()).hexdigest()
        user = getUser(username)

        if user is None:
            flash("Username not found.", category="error")
        elif loginHashedPassword != user[2]:
            flash("Incorrect password.", category="error")
        else:
            flash("Logged in successfully!", category="success")
            objUser = User(*user)
            login_user(objUser)
            return redirect('/dashboard')

    return render_template("login.html", boolean=True)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

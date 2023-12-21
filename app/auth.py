from flask import Blueprint, redirect, render_template, request, flash
from flask_login import login_user, login_required, logout_user, current_user
import hashlib
from . import mysql
from .queries import getUser, insertUser
from .models import User

auth = Blueprint("auth", __name__)

#If no route is selected, automatically directs user to login page
@auth.route("/")
def default():
    return redirect("/login")

@auth.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        username = request.form.get("username")
        password = request.form.get("password")

        existingUser = getUser(username)

        #Prerequisite checks for user creating an account

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
            #Hashes password inputted
            hashedPassword = hashlib.sha256(password.encode()).hexdigest()

            #Inserts user into user database
            insertUser(username, hashedPassword, firstName, lastName, "test")
            newUser = getUser(username)
            
            #Logs user into account and redirects user to dashboard page
            #if user is properly inserted into database
            if newUser:
                objUser = User(*newUser)
                login_user(objUser)
                flash("Account created!", category="success")
                return redirect("/dashboard")
            else:
                flash("Error creating account.", category="error")

    return render_template("signup.html", user=current_user)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")


        #Hashes password inputted
        loginHashedPassword = hashlib.sha256(password.encode()).hexdigest()
        user = getUser(username)

        #Prerequisite checks for user logging into their account

        if user is None:
            flash("Username not found.", category="error")
        #Checks if inputted password doesn't equal to passsword stored in user database
        elif loginHashedPassword != user[2]:
            flash("Incorrect password.", category="error")
        #Logs user into account and redirects user to dashboard page
        else:
            objUser = User(*user)
            login_user(objUser)
            flash("Logged in successfully!", category="success")
            return redirect("/dashboard")

    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

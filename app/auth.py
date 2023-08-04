from flask import Blueprint, redirect, render_template

auth = Blueprint('auth', __name__)

@auth.route('/')
def default():
    return redirect('/login')

@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/signup')
def sign_up():
    return render_template("signup.html")

@auth.route('/logout')
def logout():
    return "<p>Logout<p>"

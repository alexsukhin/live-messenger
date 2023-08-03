from flask import Blueprint, redirect

auth = Blueprint('auth', __name__)

@auth.route('/')
def default():
    return redirect('/login')

@auth.route('/login')
def login():
    return "<p>Login<p>"

@auth.route('/signup')
def sign_up():
    return "<p>Sign up<p>"

@auth.route('/logout')
def logout():
    return "<p>Logout<p>"

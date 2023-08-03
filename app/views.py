from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/dashboard')
def dashboard():
    return "<h1>dashboard<h1>"

@views.route('/profile')
def profile():
    return "<h1>profile<h1>"
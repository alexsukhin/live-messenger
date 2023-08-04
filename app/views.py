from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@views.route('/profile')
def profile():
    return render_template("profile.html")
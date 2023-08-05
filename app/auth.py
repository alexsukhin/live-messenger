from flask import Blueprint, redirect, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/')
def default():
    return redirect('/login')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html", boolean=True)

@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        username = request.form.get("username")
        password = request.form.get("password")

        if len(firstName) > 24:
            flash("First name must be less than 25 characters.", category="error")
        elif len(lastName) > 24:
            flash("Last name must be less than 25 characters.", category="error")
        elif len(username) > 14:
            flash("Username must be less than 15 characters.", category="error")
        elif len(password) > 49:
            flash("Password must be less than 50 characters.", category="error")
        else:
            flash("Account created!", category="success")

    return render_template("signup.html")

@auth.route('/logout')
def logout():
    return "<p>Logout<p>"

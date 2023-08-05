from flask import Blueprint, redirect, render_template, request, flash
from . import mysql
import hashlib


auth = Blueprint('auth', __name__)

def insert_user(Username, Password, firstName, lastName, PublicRSAKey):
    
    HashedPassword = hashlib.sha256(Password.encode()).hexdigest()

    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO users (Username, HashedPassword, FirstName, LastName, PublicRSAKey) VALUES (%s, %s, %s, %s, %s);"
    values = (Username, HashedPassword, firstName, lastName, PublicRSAKey)
    #print("SQL query:", cursor.mogrify(sql, values))  # This will print the formatted query
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()  

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

        if len(firstName) > 25:
            flash("First name must be 25 characters or less.", category="error")
        elif len(lastName) > 25:
            flash("Last name must be 25 characters or less.", category="error")
        elif len(username) > 15:
            flash("Username must be 15 characters or less.", category="error")
        elif len(password) > 50:
            flash("Password must be 50 characters or less.", category="error")
        else:
            insert_user(username, password, firstName, lastName, 'test')
            flash("Account created!", category="success")
            return redirect('/dashboard')

    return render_template("signup.html")
    

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html", boolean=True)


@auth.route('/logout')
def logout():
    return "<p>Logout<p>"

from flask import Blueprint, redirect, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .queries import getUser, insertConnection, connectionExists, getChatUsers, updateName, updateUsername, updatePasword
import hashlib

views = Blueprint('views', __name__)

@views.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == "POST":
        username = request.form.get("username")
        recipient = getUser(username)

        senderID = current_user.id

        if recipient is None:
            flash("Username not found.", category="error")
        else:
            recipientID = recipient[0]

            if connectionExists(senderID, recipientID) == True:
                flash("User already exists in your chat list.", category="error")
            elif senderID == recipientID:
                flash("You cannot add yourself.", category="error")
            else:
                insertConnection(senderID, recipientID)
                flash("Successfully added user!", category="success")

    return render_template("dashboard.html", user=current_user)

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == "POST":
        if "changeName" in request.form:
            firstName = request.form.get("firstName")
            lastName = request.form.get("lastName")

            if len(firstName) > 25:
                flash("First name must be 25 characters or less.", category="error")
            elif len(lastName) > 25:
                flash("Last name must be 25 characters or less.", category="error")
            else:
                updateName(current_user.id, firstName, lastName)
                flash("Successfully updated user's name!", category="success")
                return redirect('/profile')
        
        elif "changeUsername" in request.form:
            username = request.form.get("username")
            existingUser = getUser(username)

            if existingUser:    
                flash("Username already exists", category="error")
            elif len(username) > 15:
                flash("Username must be 15 characters or less.", category="error")
            else:
                updateUsername(current_user.id, username)
                flash("Successfully updated username!", category="success")
                return redirect('/profile')

        elif "changePassword" in request.form:
            currentPassword = request.form.get("currentPassword")
            newPassword = request.form.get("newPassword")
            currentHashedPassword = hashlib.sha256(currentPassword.encode()).hexdigest()

            if currentHashedPassword != current_user.password:
                flash("Your current password is incorrect.", category="error")
            elif len(newPassword) > 50:
                flash("Password must be 50 characters or less.", category="error")
            else:
                updatePasword(current_user.id, newPassword)
                flash("Successfully updated password!", category="success")
                return redirect('/profile')

    return render_template("profile.html", user=current_user)

@views.route('/get-chat-users')
@login_required
def get_chat_users():
    chatUsers = getChatUsers(current_user.id)
    return jsonify(chatUsers)
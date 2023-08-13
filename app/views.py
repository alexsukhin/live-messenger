from flask import Blueprint, redirect, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .queries import getUser, insertConnection, connectionExists, getChatUsers

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

@views.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@views.route('/get-chat-users')
@login_required
def get_chat_users():
    chatUsers = getChatUsers(current_user.id)
    return jsonify(chatUsers)
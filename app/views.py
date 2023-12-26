from flask import Blueprint, redirect, render_template, request, flash, jsonify, session
from flask_login import login_required, current_user
from .queries import *
import hashlib
import base64

views = Blueprint("views", __name__)

@views.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        #Adds a new user to chat list for communication through 'Add User' button
        if "username" in request.form:
            username = request.form.get("username")
            recipient = getUser(username)

            senderID = current_user.id

            #Prerequisite checks for validation for adding a new user

            if recipient is None:
                flash("Username not found.", category="error")
            else:
                #Gets the recipientID from 'recipient' user object
                recipientID = recipient[0]

                if connectionExists(senderID, recipientID) == True:
                    flash("User already exists in your chat list.", category="error")
                elif senderID == recipientID:
                    flash("You cannot add yourself.", category="error")
                #Inserts new user into connections database
                else:
                    insertConnection(senderID, recipientID)
                    flash("Successfully added user!", category="success")

    return render_template("dashboard.html", user=current_user)

@views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        if "changeName" in request.form:
            firstName = request.form.get("firstName")
            lastName = request.form.get("lastName")

            #Prerequisite checks for updating user's name

            if len(firstName) > 25:
                flash("First name must be 25 characters or less.", category="error")
            elif len(lastName) > 25:
                flash("Last name must be 25 characters or less.", category="error")
            else:
                updateName(current_user.id, firstName, lastName)
                flash("Successfully updated user's name!", category="success")
                return redirect("/profile")

        elif "changeUsername" in request.form:
            username = request.form.get("username")
            existingUser = getUser(username)

            #Prerequisite checks for updating user's username

            if existingUser:
                flash("Username already exists", category="error")
            elif len(username) > 15:
                flash("Username must be 15 characters or less.", category="error")
            else:
                updateUsername(current_user.id, username)
                flash("Successfully updated username!", category="success")
                return redirect("/profile")

        elif "changePassword" in request.form:
            currentPassword = request.form.get("currentPassword")
            newPassword = request.form.get("newPassword")

            #Hashes user's inputted current password
            currentHashedPassword = hashlib.sha256(currentPassword.encode()).hexdigest()

            #Prerequisite checks for updating user's password

            if currentHashedPassword != current_user.password:
                flash("Your current password is incorrect.", category="error")
            elif len(newPassword) > 50:
                flash("Password must be 50 characters or less.", category="error")
            else:
                updatePassword(current_user.id, newPassword)
                flash("Successfully updated password!", category="success")
                return redirect("/profile")

    return render_template("profile.html", user=current_user)

#Creating HTML routes for SQL queries
#Encrypted data is stored in routes

#HTML route for inserting a new message into messages database
@views.route("/insert-message/<sessionID>/<recipientID>/<encryptedContent>/<IV>/<dataFormat>")
@login_required
def insert_message(sessionID, recipientID, encryptedContent, IV, dataFormat):
    insertMessage(sessionID, current_user.id, recipientID, encryptedContent, IV, dataFormat)
    return jsonify({"message": "Message inserted successfully"})

#HTML route for inserting a new session into sessions database
@views.route("/insert-session/<conversationID>/<encryptedAESKey>")
@login_required
def insert_session(conversationID, encryptedAESKey):
    insertSession(conversationID, encryptedAESKey)
    return jsonify({"message": "Session inserted successfully"})

#HTML route for inserting a new conversation into conversations database
@views.route("/insert-conversation/<connectionID>")
@login_required
def insert_conversation(connectionID):
    insertConversation(connectionID)
    return jsonify({"message": "Conversation inserted successfully"})

#HTML route for updating the timestamp in conversations database
@views.route("/update-conversation/<conversationID>")
@login_required
def update_session(conversationID):
    updateConversation(conversationID)
    return jsonify({"message": "Conversation timestamp updated successfully"})

#HTML route for checking if user already has a conversation with another user
@views.route("/check-conversation/<connectionID>")
@login_required
def check_conversation(connectionID):
    if conversationExists(connectionID):
        return jsonify(True)
    else:
        return jsonify(False)

#HTML route for getting user's ID
@views.route("/get-sender-id")
@login_required
def get_id():
    id = current_user.id
    return jsonify(id)

    
#HTML route for getting connection ID between two users
@views.route("/get-connection-id/<recipientID>")
@login_required
def get_connection_id(recipientID):
    connectionID = getConnectionID(current_user.id, recipientID)
    return jsonify(connectionID)

#HTML route for getting latest session ID between two users
@views.route("/get-latest-session-id/<conversationID>")
@login_required
def get_latest_session_id(conversationID):
    sessionID = getLatestSessionID(conversationID)
    return jsonify(sessionID)

#HTML route for getting latest conversation ID between two users
@views.route("/get-conversation-id/<connectionID>")
@login_required
def get_conversation_id(connectionID):
    conversationID = getConversationID(connectionID)
    return jsonify(conversationID)

#HTML route for getting all messages within a conversation to retrieve chat history
@views.route("/get-chat-messages/<recipientID>")
@login_required
def get_chat_messages(recipientID):
    messages = getChatMessages(current_user.id, recipientID)
    
    for message in messages:
        if message["dataFormat"] != "text/short":
            #read file and write to encryptedContent in message
            with open(message["filePath"], "rb") as file:
                encryptedContent = file.read()

                #https://stackoverflow.com/questions/23164058/how-to-encode-text-to-base64-in-python
                base64Data = base64.b64encode(encryptedContent).decode('utf-8')
                message["encryptedContent"] = base64Data


    return jsonify(messages)

#HTML route for getting chat users for chat list in dashboard
@views.route("/get-chat-users")
@login_required
def get_chat_users():
    chatUsers = getChatUsers(current_user.id)
    return jsonify(chatUsers)
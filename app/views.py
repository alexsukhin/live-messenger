from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .queries import *
import base64


views = Blueprint("views", __name__)

#Creating HTML routes for SQL queries
#Encrypted data is stored in routes

#HTML route for inserting a new session into sessions database
@views.route("/insert-session/<conversationID>", methods=["POST"])
@login_required
def insert_session(conversationID):
        data = request.get_json()
        senderEncryptedAESKey = data.get("senderEncryptedAESKey")
        recipientEncryptedAESKey = data.get("recipientEncryptedAESKey")

        insertSession(conversationID, senderEncryptedAESKey, recipientEncryptedAESKey)

        return jsonify({"message": "Session inserted successfully"})

#HTML route for inserting a new conversation into conversations database
@views.route("/insert-conversation/<connectionID>")
@login_required
def insert_conversation(connectionID):
    insertConversation(connectionID)
    return jsonify({"message": "Conversation inserted successfully"})

#HTML route for updating the timestamp in conversations database
@views.route("/update-RSA-public-key/<publicRSAKey>")
@login_required
def update_RSA_public_key(publicRSAKey):
    updateRSAPublicKey(current_user.id, publicRSAKey)
    return jsonify({"message": "Updated public RSA key successfully"})

@views.route("/update-conversation/<conversationID>")
@login_required
def update_conversation(conversationID):
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

#HTML route for getting latest conversation ID between two users
@views.route("/get-conversation-id/<connectionID>")
@login_required
def get_conversation_id(connectionID):
    conversationID = getConversationID(connectionID)
    return jsonify(conversationID)

#HTML route for getting latest session ID between two users
@views.route("/get-latest-session-id/<conversationID>")
@login_required
def get_latest_session_id(conversationID):
    sessionID = getLatestSessionID(conversationID)
    return jsonify(sessionID)

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
                base64Data = base64.b64encode(encryptedContent).decode("utf-8")
                message["content"] = base64Data


    return jsonify(messages)

#HTML route for getting chat users for chat list in dashboard
@views.route("/get-chat-users")
@login_required
def get_chat_users():
    chatUsers = getChatUsers(current_user.id)
    return jsonify(chatUsers)


@views.route("/get-RSA-public-key/<recipientID>")
@login_required
def get_RSA_public_key(recipientID):
    RSAPublicKey = getRSAPublicKey(recipientID)
    print(RSAPublicKey)
    return jsonify(RSAPublicKey[0])

@views.route("/get-encrypted-AES-key/<userID>")
@login_required
def get_encrypted_AES_key(userID):
    encryptedAESKeyDict = getEncryptedAESKey(userID)

    #Sends encryptedAESKeys as base64 strings in a dictionary
    return jsonify(encryptedAESKeyDict)
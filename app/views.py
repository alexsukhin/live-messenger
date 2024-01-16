from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .queries import *
import base64


views = Blueprint("views", __name__)

#Creating HTML routes for SQL queries
#Encrypted data is stored in routes

#HTML route for inserting a new session into sessions database
@views.route("/insert-session/<conversationID>/<senderID>/<recipientID>/<cipher>", methods=["POST"])
@login_required
def insert_session(conversationID, senderID, recipientID, cipher):
    data = request.get_json()
    senderEncryptedAESKey = data.get("senderEncryptedAESKey")
    recipientEncryptedAESKey = data.get("recipientEncryptedAESKey")

    insertSession(conversationID, senderID, recipientID, cipher, senderEncryptedAESKey, recipientEncryptedAESKey)

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

#HTML route for updating the timestamp in conversations database
@views.route("/update-RSA-private-key/<privateRSAKey>")
@login_required
def update_RSA_private_key(privateRSAKey):
    updateRSAPrivateKey(current_user.id, privateRSAKey)
    return jsonify({"message": "Updated private RSA key successfully"})

#HTML route for updating the timestamp in conversations database
@views.route("/update-conversation/<conversationID>")
@login_required
def update_conversation(conversationID):
    updateConversation(conversationID)
    return jsonify({"message": "Conversation timestamp updated successfully"})


@views.route("/update-AES-cipher")
@login_required
def update_AES_cipher():
    updateAESCipher(current_user.id)
    return jsonify({"message": "Updated cipher to AES-RSA"})

@views.route("/update-XOR-cipher")
@login_required
def update_XOR_cipher():
    updateXORCipher(current_user.id)
    return jsonify({"message": "Updated cipher to XOR"})

@views.route("/update-XOR-hashed-password/<hashedPassword>/<conversationID>")
@login_required
def update_XOR_hashed_password(hashedPassword, conversationID):
    updateXORHashedPassword(hashedPassword, conversationID)
    return jsonify({"message": "Updated XOR Hashed Password"})


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
    senderConnectionID = getConnectionID(current_user.id, recipientID)
    recipientConnectionID = getConnectionID(recipientID, current_user.id)
    return jsonify(senderConnectionID, recipientConnectionID)

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

@views.route("/get-session-data/<sessionID>")
@login_required
def get_session_data(sessionID):
    sessionID = getSessionData(sessionID)
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


@views.route("/get-RSA-public-key/<userID>")
@login_required
def get_RSA_public_key(userID):
    RSAPublicKey = getRSAPublicKey(userID)
    return jsonify(RSAPublicKey[0])

@views.route("/get-RSA-private-key")
@login_required
def get_RSA_private_key():
    RSAPrivateKey = getRSAPrivateKey(current_user.id)
    return jsonify(RSAPrivateKey[0])

@views.route("/get-encrypted-AES-key/<sessionID>")
@login_required
def get_encrypted_AES_key(sessionID):
    encryptedAESKeyDict = getEncryptedAESKey(sessionID)

    #Sends encryptedAESKeys as base64 strings in a dictionary
    return jsonify(encryptedAESKeyDict)

@views.route("/get-cipher/<userID>")
@login_required
def get_cipher(userID):
    cipher = getCipher(userID)

    return jsonify(cipher[0])

@views.route("/get-XOR-hashed-password/<conversationID>")
@login_required
def get_XOR_hashed_password(conversationID):
    XORHashedPassword = getXORHashedPassword(conversationID)

    return jsonify(XORHashedPassword[0])
    
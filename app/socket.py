from flask_socketio import SocketIO, join_room
from flask_login import current_user
from .queries import insertMessage

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    room_id = f"room_{current_user.id}"
    print(room_id)
    join_room(room_id)

@socketio.on('message')
def handle_message(sessionID, recipientID, encryptedContent, IV, dataFormat):
    senderID = current_user.id

    #Stores message in messages database for retrieval when user opens chat
    insertMessage(sessionID, senderID, recipientID, encryptedContent, IV, dataFormat)

    message = {
        "senderID": senderID,
        "encryptedContent": encryptedContent
        }   

    #Emits message to javascript client to push messages in real time

    socketio.emit('message', message, room=f"room_{senderID}")
    
    socketio.emit('message', message, room=f"room_{recipientID}")
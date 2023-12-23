from flask_socketio import SocketIO, join_room
from flask_login import current_user
from .queries import insertMessage

socketio = SocketIO()

def room_exists(room_name):
    rooms_dict = socketio.server.manager.rooms

    if room_name in rooms_dict['/']:
        return True
    else:
        return False

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
        "recipientID": recipientID,
        "encryptedContent": encryptedContent
        }

    #Emits message to javascript client to push messages in real time
    if room_exists(f"room_{senderID}"):
        socketio.emit('message', message, room=f"room_{senderID}")

    if room_exists(f"room_{recipientID}"):
        socketio.emit('message', message, room=f"room_{recipientID}")
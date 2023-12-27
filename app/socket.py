from flask_socketio import SocketIO, join_room
from flask_login import current_user
from .queries import insertMessage, insertFile
import base64
from datetime import datetime

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
def handle_message(sessionID, recipientID, encryptedContent, dataFormat):
    senderID = current_user.id

    #Stores message in messages database for retrieval when user opens chat
    if insertMessage(sessionID, senderID, recipientID, encryptedContent, dataFormat):

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


@socketio.on('file')
def handle_file(sessionID, recipientID, encryptedContent, fileName, dataFormat, IV):
    senderID = current_user.id

    time = datetime.now()
    fileName = str(time.hour) + str(time.minute) + str(time.second) + "%" + str(fileName)
    filePath = "D:\\Live Messenger\\files\\" + fileName


    #https://stackoverflow.com/questions/23164058/how-to-encode-text-to-base64-in-python
    base64Data = base64.b64encode(encryptedContent).decode('utf-8')
    
    if insertFile(sessionID, senderID, recipientID, filePath, dataFormat, IV):
        with open(filePath, "wb") as file:
            file.write(encryptedContent)

        file = {
            "senderID": senderID,
            "recipientID": recipientID,
            "encryptedContent": base64Data,
            "filePath" : filePath,
            "dataFormat": dataFormat,
            "IV": IV
        }

        if room_exists(f"room_{senderID}"):
            socketio.emit('file', file, room=f"room_{senderID}")

        if room_exists(f"room_{recipientID}"):
            socketio.emit('file', file, room=f"room_{recipientID}")
    else:
        print("Failed to insert file, possibly too big")
        #fix file size issue

    #do file communication (txt, pdf) - tmrw
    #allow users to download files - tmrw or day after
    #implement encryption, possibly multiple encryptions - not sure how long, 3-5 days
    #update analysis, design
    #start technical solution after holiday or before if time
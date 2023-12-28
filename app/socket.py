from flask_socketio import SocketIO, join_room
from flask_login import current_user
from .queries import insertMessage, insertFile, incrementNotificationCounter, resetNotificationCounter, getNotificationCounter
import base64
from datetime import datetime

socketio = SocketIO()


def room_exists(room_name):
    #Gets list of current online rooms
    rooms_dict = socketio.server.manager.rooms

    #Checks if room is in list, representing if user is online
    if room_name in rooms_dict['/']:
        return True
    else:
        return False

@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('join-room')
def handle_joinroom(recipientID):
    room_id = f"room_{current_user.id}_{recipientID}"

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
        #Emits message to both sender and recipient if they are online
        if room_exists(f"room_{senderID}_{recipientID}"):
            socketio.emit('message', message, room=f"room_{senderID}_{recipientID}")

        if room_exists(f"room_{recipientID}_{senderID}"):
            socketio.emit('message', message, room=f"room_{recipientID}_{senderID}")


@socketio.on('file')
def handle_file(sessionID, recipientID, encryptedContent, fileName, dataFormat, IV):

    senderID = current_user.id

    #Creates unique identifier for file name based on current time
    time = datetime.now()
    fileName = str(time.hour) + str(time.minute) + str(time.second) + "%" + str(fileName)

    #Sets file path location for server storage
    filePath = "D:\\Live Messenger\\files\\" + fileName

    #Encodes array buffer to base 64 string
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
        #Emits message to javascript client to push messages in real time
        #Emits message to both sender and recipient if they are online
        if room_exists(f"room_{senderID}_{recipientID}"):
            socketio.emit('file', file, room=f"room_{senderID}_{recipientID}")

        if room_exists(f"room_{recipientID}_{senderID}"):
            socketio.emit('file', file, room=f"room_{recipientID}_{senderID}")
    else:
        print("Failed to insert file, possibly too big")
        #fix file size issue

@socketio.on('reset-notification')
def reset_notification_counter(recipientID):

    senderID = current_user.id

    #Sets notification counter to 0 in connections database
    resetNotificationCounter(senderID, recipientID)

    socketio.emit('reset-notification', room=f"room_{senderID}_{recipientID}")



@socketio.on('increment-notification')
def increment_notification_counter(recipientID):

    senderID = current_user.id

    #Increments notification counter by one if the recipient's room doesn't exist
    if (room_exists(f"room_{recipientID}_{senderID}") == False):
        incrementNotificationCounter(senderID, recipientID)


#implemented notification counter, possibly fix query so highlighted user goes to top (after encryption)
#implement encryption, possibly multiple encryptions - not sure how long, give myself 5 days
#update analysis, design
#start technical solution after holiday or before if time
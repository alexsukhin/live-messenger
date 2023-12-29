from flask_socketio import SocketIO, join_room
from flask_login import current_user
from .queries import insertMessage, insertFile, incrementNotificationCounter, resetNotificationCounter, getNotificationCounter
import base64
from datetime import datetime

class ChatSocketIO(SocketIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_connect(self):
        pass

    def handle_joinroom(self, recipientID):
        room_id = f"room_{current_user.id}_{recipientID}"
        join_room(room_id)

    def room_exists(self, room_name):
        #Gets list of current online rooms
        rooms_dict = self.server.manager.rooms

        #Checks if room is in list, representing if user is online
        if room_name in rooms_dict['/']:
            return True
        else:
            return False
    
    def emit_message(self, event, data, room):
        #Emits message to javascript client to push messages in real time
        if self.room_exists(room):
            self.emit(event, data, room=room)


    def handle_message(self, sessionID, recipientID, encryptedContent, dataFormat):
        senderID = current_user.id

        #Stores message in messages database for retrieval when user opens chat
        if insertMessage(sessionID, senderID, recipientID, encryptedContent, dataFormat):
            message = {
                "senderID": senderID,
                "recipientID": recipientID,
                "encryptedContent": encryptedContent
            }

        #Emits message to both sender and recipient if they are online
        self.emit_message("message", message, f"room_{senderID}_{recipientID}")
        self.emit_message("message", message, f"room_{recipientID}_{senderID}")

    def handle_file(self, sessionID, recipientID, encryptedContent, fileName, dataFormat, IV):
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

            #Emits message to both sender and recipient if they are online
            self.emit_message("file", file, f"room_{senderID}_{recipientID}")
            self.emit_message("file", file, f"room_{recipientID}_{senderID}")
        else:
            print("Failed to insert file, possibly too big")
            #fix file size issue

    def reset_notification_counter(self, recipientID):
        senderID = current_user.id
        
        #Sets notification counter to 0 in connections database
        resetNotificationCounter(senderID, recipientID)

        self.emit('reset-notification', room=f"room_{senderID}_{recipientID}")

    def increment_notification_counter(self, recipientID):

        senderID = current_user.id

        #Increments notification counter by one if the recipient's room doesn't exist
        if (self.room_exists(f"room_{recipientID}_{senderID}") == False):
            incrementNotificationCounter(senderID, recipientID)

#Creating instance of socket
socketio = ChatSocketIO()

#Event handlers
socketio.on_event('connect', socketio.handle_connect)
socketio.on_event('join-room', socketio.handle_joinroom)
socketio.on_event('message', socketio.handle_message)
socketio.on_event('file', socketio.handle_file)
socketio.on_event('reset-notification', socketio.reset_notification_counter)
socketio.on_event('increment-notification', socketio.increment_notification_counter)


#implemented notification counter, possibly fix query so highlighted user goes to top (after encryption)
#implement encryption, possibly multiple encryptions - not sure how long, give myself 5 days
#update analysis, design
#start technical solution after holiday or before if time

#refactor code into oop

#then implement encryption using new oop system, 
import hashlib
from . import mysql

#INSERT queries

def insertUser(username, password, firstName, lastName, publicRSAKey):
    
    hashedPassword = hashlib.sha256(password.encode()).hexdigest()

    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO users (Username, HashedPassword, FirstName, LastName, PublicRSAKey) VALUES (%s, %s, %s, %s, %s);"
    values = (username, hashedPassword, firstName, lastName, publicRSAKey,)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()  

def insertConnection(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO connections (SenderID, RecipientID) VALUES (%s, %s);"
    values = (senderID, recipientID)
    cursor.execute(sql, values)

    sql = "INSERT INTO connections (RecipientID, SenderID) VALUES (%s, %s);"
    values = (senderID, recipientID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

def insertConversation(connectionID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO conversations (ConnectionID) VALUES (%s);"
    cursor.execute(sql, (connectionID,))

    conn.commit()
    cursor.close()

def insertSession(conversationID, encryptedAESKey, socketID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO sessions (ConversationID, EncryptedAESKey, SocketID) VALUES (%s, %s, %s);"
    values = (conversationID, encryptedAESKey, socketID,)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

def insertMessage(sessionID, senderID, recipientID, encryptedContent, IV, dataFormat):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO messages (SessionID, SenderID, RecipientID, EncryptedContent, IV, DataFormat) VALUES (%s, %s, %s, %s, %s, %s);"
    values = (sessionID, senderID, recipientID, encryptedContent, IV, dataFormat,)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()  


#UPDATE queries

def updateName(userID, firstName, lastName):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE users SET FirstName = %s, LastName = %s WHERE UserID = %s;"
    values = (firstName, lastName, userID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

def updateUsername(userID, newUsername):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE users SET Username = %s WHERE UserID = %s;"
    values = (newUsername, userID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

def updatePassword(userID, password):

    hashedPassword = hashlib.sha256(password.encode()).hexdigest()

    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE users SET HashedPassword = %s WHERE UserID = %s;"
    values = (hashedPassword, userID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

def updateConversation(conversationID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE conversations SET Timestamp = now() WHERE ConversationID = %s;"
    cursor.execute(sql, (conversationID,))

    conn.commit()
    cursor.close()


#SELECT queries

def getUser(username):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE Username = %s"
    cursor.execute(sql, (username,))
    user = cursor.fetchone()

    cursor.close()
    return user

def getChatUsers(userID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT UserID, Username, FirstName, LastName, NotificationCounter, c.Timestamp, co.Timestamp
    FROM users u
    JOIN connections c ON (c.RecipientID = u.UserID)
    LEFT JOIN conversations co ON (c.connectionID = co.connectionID)
    WHERE (c.SenderID = %s) AND u.UserID != %s
    ORDER BY NotificationCounter DESC, co.Timestamp DESC, c.Timestamp DESC;"""
    cursor.execute(sql, (userID, userID,))
    chatUsers = cursor.fetchall()

    cursor.close()
    
    chatUsersList = []

    for user in chatUsers:
        chatUsersDict = {
            "userID": user[0],
            "username": user[1],
            "firstName": user[2],
            "lastName": user[3],
            "notificationCounter": user[4]
        }
        
        chatUsersList.append(chatUsersDict)



    return chatUsersList

def getChatMessages(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql="""SELECT SenderID, EncryptedContent FROM messages
    WHERE (SenderID = %s AND RecipientID = %s)
    OR (SenderID = %s AND RecipientID = %s)
    ORDER BY Timestamp ASC;"""
    cursor.execute(sql, (senderID, recipientID, recipientID, senderID))
    messages = cursor.fetchall()

    cursor.close()

    messagesList = []

    for message in messages:
        messageDict = {
            "senderID": message[0],
            "encryptedContent": message[1]
        }
        
        messagesList.append(messageDict)

    return messagesList

def connectionExists(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT COUNT(*) FROM connections
    WHERE (SenderID = %s AND RecipientID = %s);"""
    cursor.execute(sql, (senderID, recipientID,))
    connection = cursor.fetchone()

    cursor.close()

    if connection[0] > 0:
        return True
    else:
        return False

def getConnectionID(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT ConnectionID FROM connections
    WHERE (SenderID = %s AND RecipientID = %s);"""
    cursor.execute(sql, (senderID, recipientID,))
    connectionID = cursor.fetchone()

    cursor.close()

    return connectionID

def conversationExists(connectionID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT COUNT(*) from conversations
    WHERE ConnectionID = %s;"""
    cursor.execute(sql, (connectionID,))
    conversation = cursor.fetchone()

    cursor.close()

    if conversation[0] > 0:
        return True
    else:
        return False

def getConversationID(connectionID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT ConversationID FROM conversations
    WHERE ConnectionID = %s;"""
    cursor.execute(sql, (connectionID,))
    conversationID = cursor.fetchone()

    cursor.close()  

    return conversationID

def getLatestSessionID(conversationID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT SessionID
    FROM sessions
    WHERE ConversationID = %s
    ORDER BY SessionID DESC
    LIMIT 1;"""
    cursor.execute(sql, (conversationID,))
    sessionID = cursor.fetchone()

    cursor.close()

    return sessionID    
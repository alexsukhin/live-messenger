import hashlib
from . import mysql

#INSERT queries

#Inserts a new user on signup into users database
def insertUser(username, password, firstName, lastName):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO users (Username, HashedPassword, FirstName, LastName, Cipher) VALUES (%s, %s, %s, %s, %s);"
    values = (username, password, firstName, lastName, "AES-RSA")
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()  

#Inserts a new connection when user adds another user into connections database
def insertConnection(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    #Inserts two connections into database for both permutations

    sql = "INSERT INTO connections (SenderID, RecipientID) VALUES (%s, %s);"
    values = (senderID, recipientID)
    cursor.execute(sql, values)

    sql = "INSERT INTO connections (RecipientID, SenderID) VALUES (%s, %s);"
    values = (senderID, recipientID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

#Inserts a new message into messages database
def insertMessage(sessionID, encryptedContent, dataFormat, IV, salt):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO messages (SessionID, EncryptedContent, DataFormat, IV, Salt) VALUES (%s, %s, %s, %s, %s);"
    values = (sessionID, encryptedContent, dataFormat, IV, salt)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

    return True

#Inserts a new file into messages database
def insertFile(sessionID, filePath, dataFormat, IV, salt):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO messages (SessionID, FilePath, DataFormat, IV, Salt) VALUES (%s, %s, %s, %s, %s);"
    values = (sessionID, filePath, dataFormat, IV, salt)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

    return True
    

#Inserts a new session when user opens a chat session into sessions database
def insertSession(conversationID, senderID, recipientID, cipher, senderEncryptedAESKey, recipientEncryptedAESKey):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO sessions (ConversationID, SenderID, RecipientID, cipher, SenderEncryptedAESKey, RecipientEncryptedAESKey) VALUES (%s, %s, %s, %s, %s, %s);"
    values = (conversationID, senderID, recipientID, cipher, senderEncryptedAESKey, recipientEncryptedAESKey)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

#Inserts a new conversation when user opens a chat session for the first time into conversations database
def insertConversation(connectionID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO conversations (ConnectionID) VALUES (%s);"
    cursor.execute(sql, (connectionID,))

    conn.commit()
    cursor.close()

#UPDATE queries

#Updates user's username from profile page
def updateUsername(userID, newUsername):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE users SET Username = %s WHERE UserID = %s;"
    values = (newUsername, userID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

#Updates user's name from profile page
def updateName(userID, firstName, lastName):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE users SET FirstName = %s, LastName = %s WHERE UserID = %s;"
    values = (firstName, lastName, userID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

#Updates user's password from profile page
def updatePassword(userID, password):

    hashedPassword = hashlib.sha256(password.encode()).hexdigest()

    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE users SET HashedPassword = %s WHERE UserID = %s;"
    values = (hashedPassword, userID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

#Updates the timestamp in conversations database
def updateConversation(conversationID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE conversations SET Timestamp = now() WHERE ConversationID = %s;"
    cursor.execute(sql, (conversationID,))

    conn.commit()
    cursor.close()

#Increases notification counter by one when sender sends a message to a recipient
def incrementNotificationCounter(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """UPDATE connections
    SET NotificationCounter = NotificationCounter + 1
    WHERE (SenderID = %s AND RecipientID = %s);"""
    values = (recipientID, senderID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

#Resets notification counter to zero
def resetNotificationCounter(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()
    
    sql = """UPDATE connections
    SET NotificationCounter = 0
    WHERE (SenderID = %s AND RecipientID = %s);"""
    values = (senderID, recipientID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

#Updates null RSA placeholder with public RSA key
def updateRSAPublicKey(userID, publicRSAKey):

    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE users SET PublicRSAKey = %s WHERE UserID = %s;"
    values = (publicRSAKey, userID)
    cursor.execute(sql, values)
    
    conn.commit()
    cursor.close()

#test purpose
def updateRSAPrivateKey(userID, privateRSAKey):
    
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "UPDATE users SET PrivateRSAKey = %s WHERE UserID = %s;"
    values = (privateRSAKey, userID)
    cursor.execute(sql, values)
    
    conn.commit()
    cursor.close()

#Sets cipher in users database to AES-RSA
def updateAESCipher(senderID):
    conn = mysql.connection
    cursor = conn.cursor()
    
    sql = """UPDATE users
    SET Cipher = "AES-RSA"
    WHERE (UserID = %s);"""
    values = (senderID,)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

#Sets cipher in users database to XOR
def updateXORCipher(senderID):
    conn = mysql.connection
    cursor = conn.cursor()
    
    sql = """UPDATE users
    SET Cipher = "XOR"
    WHERE (UserID = %s);"""
    values = (senderID,)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

#Updates hashed XOR password to certain hashed password
def updateXORHashedPassword(XORHashedPassword, conversationID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """
    UPDATE conversations SET XORHashedPassword = %s WHERE ConversationID = %s
    """
    values = (XORHashedPassword, conversationID)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()

    return XORHashedPassword


#SELECT queries

#Checks if a user exists
def getUser(username):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE Username = %s"
    cursor.execute(sql, (username,))
    user = cursor.fetchone()

    cursor.close()
    
    print(user)
    return user

#Gets cipher currently in use from user
def getCipher(userID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """
    SELECT Cipher FROM users WHERE UserID = %s
    """
    cursor.execute(sql, (userID,))
    cipher = cursor.fetchone()

    cursor.close()

    return cipher

#Checks if user already has a connection with another user
def connectionExists(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT COUNT(*) FROM connections
    WHERE (SenderID = %s AND RecipientID = %s);"""
    cursor.execute(sql, (senderID, recipientID,))
    connection = cursor.fetchone()

    cursor.close()

    #If query returns a result greater than zero, there is a connection between two users
    if connection[0] > 0:
        return True
    else:
        return False

#Checks if a user already has a conversation with another user
def conversationExists(connectionID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT COUNT(*) from conversations
    WHERE ConnectionID = %s;"""
    cursor.execute(sql, (connectionID,))
    conversation = cursor.fetchone()

    cursor.close()

    #If query returns a result greater than zero, there is a conversation between two users
    if conversation[0] > 0:
        return True
    else:
        return False

#Getting the connection ID between two users
def getConnectionID(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT ConnectionID FROM connections
    WHERE (SenderID = %s AND RecipientID = %s);"""
    cursor.execute(sql, (senderID, recipientID,))
    connectionID = cursor.fetchone()

    cursor.close()

    return connectionID

#Getting the conversation ID between two users
def getConversationID(connectionID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT ConversationID FROM conversations
    WHERE ConnectionID = %s;"""
    cursor.execute(sql, (connectionID,))
    conversationID = cursor.fetchone()

    cursor.close()  

    return conversationID

#Getting the latest session ID between two users
def getLatestSessionID(conversationID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT MAX(SessionID) AS SessionID
    FROM sessions
    WHERE ConversationID = %s"""
    cursor.execute(sql, (conversationID,))
    sessionID = cursor.fetchone()

    cursor.close()

    return sessionID    
    
#Gets senderID and Cipher from a sessionID
def getSessionData(sessionID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """
    SELECT SenderID, Cipher FROM sessions WHERE SessionID = %s
    """
    cursor.execute(sql, (sessionID,))
    sessionData = cursor.fetchone()

    cursor.close()

    return sessionData

#Gets notification counter from connections database
def getNotificationCounter(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT NotificationCounter
    FROM connections
    WHERE (SenderID = %s AND RecipientID = %s)
    """

    values = (recipientID, senderID)
    cursor.execute(sql, values)
    notificationCounter = cursor.fetchone()

    cursor.close()

    return notificationCounter

#Selects all messages within a conversation to retrieve chat history
def getChatMessages(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql="""SELECT messages.SessionID, EncryptedContent, FilePath, DataFormat, IV, Salt
    FROM sessions, messages
    WHERE (sessions.SessionID = messages.SessionID)
    AND ((SenderID = %s AND RecipientID = %s)
    OR (SenderID = %s AND RecipientID = %s))
    ORDER BY Timestamp ASC
    """

    cursor.execute(sql, (senderID, recipientID, recipientID, senderID))
    messages = cursor.fetchall()

    cursor.close()


    messagesList = []

    #Appends individual messages each in a dictionary format into a list
    for message in messages:
        messageDict = {
            "sessionID": message[0],
            "senderID": None,
            "recipientID" : None,
            "content": message[1],
            "filePath": message[2],
            "dataFormat": message[3],
            "IV": message[4],
            "salt": message[5],
            "cipher": None
        }
        
        
        messagesList.append(messageDict)

    return messagesList

#Gets chat users for chat list in dashboard
def getChatUsers(userID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT UserID, Username, FirstName, LastName, NotificationCounter, c.Timestamp, co.Timestamp
    FROM users u
    JOIN connections c ON (c.RecipientID = u.UserID)
    LEFT JOIN conversations co ON (c.connectionID = co.connectionID)
    WHERE   (c.SenderID = %s) AND u.UserID != %s
    ORDER BY NotificationCounter DESC, co.Timestamp DESC, c.Timestamp DESC;"""
    cursor.execute(sql, (userID, userID,))
    chatUsers = cursor.fetchall()

    cursor.close()
    
    chatUsersList = []

    #Appends individual users each in a dictionary format into a list
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

#Gets RSA Public key from users database
def getRSAPublicKey(userID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """
    SELECT PublicRSAKey FROM users WHERE UserID = %s
    """
    cursor.execute(sql, (userID,))
    RSAPublicKey = cursor.fetchone()

    cursor.close()

    return RSAPublicKey

#Gets RSA Public key from users database
def getRSAPrivateKey(userID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """
    SELECT PrivateRSAKey FROM users WHERE UserID = %s
    """
    cursor.execute(sql, (userID,))
    RSAPrivateKey = cursor.fetchone()

    cursor.close()

    return RSAPrivateKey


#Gets encrypted AES keys from sessions database
def getEncryptedAESKey(sessionID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """
    SELECT SenderEncryptedAESKey, RecipientEncryptedAESKey FROM sessions WHERE SessionID = %s
    """
    cursor.execute(sql, (sessionID,))
    encryptedAESKeys = cursor.fetchone()

    cursor.close()


    AESKeyDict = {
        "senderEncryptedAESKey" : encryptedAESKeys[0],
        "recipientEncryptedAESKey" : encryptedAESKeys[1]
    }


    return AESKeyDict

#Gets hashed XOR Password
def getXORHashedPassword(conversationID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """
    SELECT XORHashedPassword FROM conversations WHERE ConversationID = %s
    """
    cursor.execute(sql, (conversationID,))
    XORHashedPassword = cursor.fetchone()

    cursor.close()

    return XORHashedPassword

def getConnections(userID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """
    SELECT RecipientID, Username FROM connections, users
    WHERE (users.UserID = connections.RecipientID)
        AND (SenderID = %s)
    """

    cursor.execute(sql, (userID,))
    connections = cursor.fetchall()

    cursor.close()

    connectionsList = []

    #Appends individual users each in a dictionary format into a list
    for connection in connections:
        connectionDict = {
            "userID": connection[0],
            "username": connection[1],
        }
        
        connectionsList.append(connectionDict)

    return connectionsList


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

    conn.commit()
    cursor.close()  

#UPDATE queries

#SELECT queries

def getUser(username):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE Username = %s"
    cursor.execute(sql, (username,))
    user = cursor.fetchone()

    cursor.close()
    return user

def connectionExists(senderID, recipientID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT COUNT(*) FROM connections
     WHERE (SenderID = %s AND RecipientID = %s)
     OR (SenderID = %s AND RecipientID = %s);"""
    cursor.execute(sql, (senderID, recipientID, recipientID, senderID))
    connection = cursor.fetchone()

    cursor.close()

    if connection[0] > 0:
        return True
    else:
        return False

def getChatUsers(userID):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = """SELECT UserID, FirstName, LastName, NotificationCounter, c.Timestamp, co.Timestamp
    FROM users u
    JOIN connections c ON (c.SenderID = u.userID OR c.RecipientID = u.userID)
    LEFT JOIN conversations co ON (c.connectionID = co.connectionID)
    WHERE (c.SenderID = %s OR c.RecipientID = %s)
    ORDER BY NotificationCounter DESC, co.Timestamp DESC, c.Timestamp DESC;"""
    cursor.execute(sql, (userID, userID,))
    chatUsers = cursor.fetchall()

    cursor.close()

    chatUsersDict = []

    #implement for loop to put users into usersdict

    chatUsersDict = {
        "userID": chatUsers[0],
        "firstName": chatUsers[1],
        "lastName": chatUsers[2]
    }

    return chatUsersDict


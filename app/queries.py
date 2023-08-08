import hashlib
from . import mysql

def getUser(username):
    conn = mysql.connection
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE Username = %s"
    cursor.execute(sql, (username,))
    user = cursor.fetchone()

    cursor.close()
    return user


def insertUser(username, password, firstName, lastName, publicRSAKey):
    
    hashedPassword = hashlib.sha256(password.encode()).hexdigest()

    conn = mysql.connection
    cursor = conn.cursor()

    sql = "INSERT INTO users (Username, HashedPassword, FirstName, LastName, PublicRSAKey) VALUES (%s, %s, %s, %s, %s);"
    values = (username, hashedPassword, firstName, lastName, publicRSAKey,)
    cursor.execute(sql, values)

    conn.commit()
    cursor.close()  

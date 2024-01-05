from flask_login import UserMixin

#User object created when user logs into dashboard
class User(UserMixin):
    def __init__(self, id, username, password, firstName, lastName, cipher, publicRSAKey, privateRSAKey):
        self.id = id
        self.username = username
        self.password = password
        self.firstName = firstName
        self.lastName = lastName
        self.cipher = cipher
        self.publicRSAKey = publicRSAKey
        self.privateRSAKey = privateRSAKey
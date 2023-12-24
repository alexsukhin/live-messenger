from flask_login import UserMixin

#User object created when user logs into dashboard
class User(UserMixin):
    def __init__(self, id, username, password, firstName, lastName, publicRSAKey):
        self.id = id
        self.username = username
        self.password = password
        self.firstName = firstName
        self.lastName = lastName
        self.publicRSAKey = publicRSAKey
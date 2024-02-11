import hashlib

class EncryptionManager():

    @staticmethod
    def hashPassword(password):
        return hashlib.sha256(password.encode()).hexdigest()

encryptionManager = EncryptionManager()
from Crypto.PublicKey import RSA
import hashlib

class EncryptionManager():

    @staticmethod
    def hashPassword(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generateKeyPair():
        key = RSA.generate(2048)
        publicKey = key.publickey().export_key(format="PEM")
        privateKey = key.export_key(format="PEM")
        return publicKey, privateKey

encryptionManager = EncryptionManager()
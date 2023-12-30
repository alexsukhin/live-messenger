class EncryptionManager {

    //https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/generateKey
    async generateRSAKeyPair() {
        const keyPair = await crypto.subtle.generateKey(
          {
            name: "RSA-OAEP",
            modulusLength: 2048,
            publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
            hash: "SHA-256",
          },
          true,
          ["encrypt", "decrypt"]
        );
    
        //Formats public key to jwk format in order store public key in database
        const publicKey = await crypto.subtle.exportKey("jwk", keyPair.publicKey)

        //Formats public key into JSON
        return {publicKey: JSON.stringify(publicKey), privateKey: keyPair.privateKey}
    }


}

export const encryptionManager = new EncryptionManager()



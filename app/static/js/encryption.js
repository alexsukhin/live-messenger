class EncryptionManager {

    //https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto
    async generateRSAKeyPair() {
        const keyPair = await crypto.subtle.generateKey(
          {
            name: "RSA-OAEP",
            modulusLength: 2048,
            publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
            hash: "SHA-256"
          },
          true,
          ["encrypt", "decrypt"]
        );
    
        //Formats public key to jwk format in order to store public key in database
        const publicKey = await crypto.subtle.exportKey("jwk", keyPair.publicKey)


        //Formats public key into JSON to store in database
        return {publicKey: JSON.stringify(publicKey), privateKey: keyPair.privateKey}
    }

    async exportPrivateKey(RSAPrivateKey) {

      const privateKey = await crypto.subtle.exportKey("jwk", RSAPrivateKey)
      return JSON.stringify(privateKey)

    }

    async importPrivateKey(RSAPrivateKey) {

      const internalRSAPrivateKey = await crypto.subtle.importKey(
        "jwk",
        RSAPrivateKey,
        {
          name: "RSA-OAEP",
          hash: "SHA-256"
        },
        false,
        ["decrypt"]
      )

      return internalRSAPrivateKey

    }


    async generateAESKey() {
      const AESKey = await crypto.subtle.generateKey(
        {
          name: "AES-CBC",
          length: 128
        },
        true,
        ["encrypt", "decrypt"]
      )

      //Formats AES key into raw format
      const rawAESKey = await crypto.subtle.exportKey("raw", AESKey)

      return rawAESKey
    }

    async encryptAESKey(AESKey, RSAPublicKey) {

      console.log('public key:', RSAPublicKey)
      
      //Converts jwk format into internal crypto web object for encryption
      const internalRSAPublicKey = await crypto.subtle.importKey(
        "jwk",
        RSAPublicKey,
        {
          name: "RSA-OAEP",
          hash: "SHA-256"
        },
        false,
        ["encrypt"]
      )

      //Encrypts AES key with public RSA key
      const encryptedAESKey = await crypto.subtle.encrypt(
        {
          name: "RSA-OAEP"
        },  
        internalRSAPublicKey,
        AESKey
      )

      return encryptedAESKey

    }

      async decryptAESKey(encryptedAESKey, RSAPrivateKey) {

        //Decrypts AES key with private RSA key
        const AESKey = await crypto.subtle.decrypt(
          {
            name: "RSA-OAEP"
          },
          RSAPrivateKey,
          encryptedAESKey
        )


        return AESKey


      }

    async encryptData(plaintext, AESKey, IV) {

      //Converts plaintext into array buffer
      const textEncoder = new TextEncoder();
      const data = textEncoder.encode(plaintext);

      //Converts AES key array buffer into internal cryptoweb object
      const internalAESKey = await crypto.subtle.importKey(
        "raw",
        AESKey,
        {
          name: "AES-CBC"
        },
        false,
        ["encrypt"]
      )

      //Encrypts data with AES key
      const encryptedContent = await crypto.subtle.encrypt(
        {
          name: "AES-CBC",
          iv: IV
        },
        internalAESKey,
        data
      )

      return encryptedContent
    }

    async encryptFile(plaintext, AESKey, IV) {

      //Converts AES key array buffer into internal cryptoweb object
      const internalAESKey = await crypto.subtle.importKey(
        "raw",
        AESKey,
        {
          name: "AES-CBC"
        },
        false,
        ["encrypt"]
      )

      //Encrypts data with AES key
      const encryptedContent = await crypto.subtle.encrypt(
        {
          name: "AES-CBC",
          iv: IV
        },
        internalAESKey,
        plaintext
      )

      return encryptedContent
    }

    async decryptData(encryptedContent, AESKey, IV) {

      //Converts AES key array buffer into internal cryptoweb object
      const internalAESKey = await crypto.subtle.importKey(
        "raw",
        AESKey,
        {
          name: "AES-CBC"
        },
        false,
        ["decrypt"]
      )

      //Decrypts data with AES key
      const decryptedContent = await crypto.subtle.decrypt(
        {
          name: "AES-CBC",
          iv: IV
        },
        internalAESKey,
        encryptedContent
      )

      //Converts data from array buffer to plaintext
      const textDecoder = new TextDecoder();
      const plaintext = textDecoder.decode(decryptedContent);

      return plaintext

    }

    async decryptImage(encryptedContent, AESKey, IV) {

      //Converts AES key array buffer into internal cryptoweb object
      const internalAESKey = await crypto.subtle.importKey(
        "raw",
        AESKey,
        {
          name: "AES-CBC"
        },
        false,
        ["decrypt"]
      )

      //Decrypts data with AES key
      const decryptedContent = await crypto.subtle.decrypt(
        {
          name: "AES-CBC",
          iv: IV
        },
        internalAESKey,
        encryptedContent
      )

      return decryptedContent
    }


}

export const encryptionManager = new EncryptionManager()



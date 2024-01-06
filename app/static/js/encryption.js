import { Base64toArrayBuffer, arrayBuffertoBase64 } from "./functions.js";

class EncryptionManager {

  async hashPassword(password) {
    const textEncoder = new TextEncoder;
    const arrayPassword = textEncoder.encode(password);
    
    const hashedPassword = await crypto.subtle.digest("SHA-256", arrayPassword)

    //https://stackoverflow.com/questions/40031688/javascript-arraybuffer-to-hex
    return [...new Uint8Array (hashedPassword)]
      .map (b => b.toString (16).padStart (2, "0"))
      .join ("");
  }

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

    return decryptedContent

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

  async deriveXORKey(password, salt) {

    const textEncoder = new TextEncoder();
    const arrayPassword = textEncoder.encode(password);

    //Converts array buffer to internal key
    const internalPassword = await crypto.subtle.importKey(
      'raw',
      arrayPassword.buffer,
      { name: 'PBKDF2' },
      false,
      ['deriveBits', 'deriveKey']
    );

    //Derives XOR key through hashed password and message salt
    const arrayDerivedKey = await crypto.subtle.deriveBits(
      {
        name: 'PBKDF2',
        salt: salt,
        iterations: 1000,
        hash: 'SHA-256',
      },
      internalPassword,
      128
    );

    return arrayDerivedKey
    
  }

  //Pad using PCKS#7 padding
  async padUint8Array(Uint8Data) { 
    //Calculates length of padding required
    const padLength = 16 - (Uint8Data.length % 16);
    //Creates a new array with length of original array + padding
    const padData = new Uint8Array(Uint8Data.length + padLength)
    //Copies original data to new pad array
    padData.set(Uint8Data)

    //Inserts the amount of padding bytes required with value of the padlength
    for (let i = Uint8Data.length; i < padData.length; i++) {
      padData[i] = padLength;
    }

    return padData;
  }

  //Unpad using PCKS#7 padding
  async unpadUint8Array(padData) {
    //Calculates length of pad used in data through value of last bit of array
    const padLength = padData[padData.length - 1];
    //Calculates original length of data by subtracting pad array with pad length
    const originalLength = padData.length - padLength;

    //Gets rid of padded data with slice function up to original length of data array
    return padData.slice(0, originalLength);
  }

  async XORCipher(Uint8Data, XORKey) {

    const Uint8Key = new Uint8Array(XORKey)

    const result = new Uint8Array(Uint8Data.length)

    //Encrypts data array inputted with XOR encryption
    for (let i = 0; i < Uint8Data.length; i++) {
      //XORs original array with key array
      //Modulo operator used to repeat key used in encryption if key is shorter than data
      result[i] = Uint8Data[i] ^ Uint8Key[i % Uint8Data.length];
    }

    return result
  } 

  async CBCEncrypt(Uint8Data, XORKey, IV) {

    //Initialises result array with length of input array
    let result = new Uint8Array(Uint8Data.length);
    let previousBlock = IV;

    for (let i = 0; i < Uint8Data.length; i += 16) {
      //Gets current block of 16 bit data
      const currentBlock = Uint8Data.slice(i, i + 16)
      //XORs current block of data with IV for first run
      //XORs current block of data with previous 'encryptedblock' for all runs after first
      const XORBlock = await encryptionManager.XORCipher(currentBlock, previousBlock)
      const encryptedBlock = await encryptionManager.XORCipher(XORBlock, XORKey)

      //Appends encrypted block to result
      result.set(encryptedBlock, i)
      previousBlock = encryptedBlock;
    }

    const base64String = await arrayBuffertoBase64(result)
  
    return base64String
  }

    // CBC Decryption
  async CBCDecrypt(ciphertext, XORKey, IV) {  


    const Uint8Data = await Base64toArrayBuffer(ciphertext)


    let result = new Uint8Array(Uint8Data.length);
    let previousBlock = IV;

    for (let i = 0; i < Uint8Data.length; i += 16) {
      //Gets current block of 16 bit data
      const currentBlock = Uint8Data.slice(i, i + 16);
      const decryptedBlock = await encryptionManager.XORCipher(currentBlock, XORKey)
      //XORs current decrypted block of data with IV for first run
      //XORs current decrypted block of data with previous 'decryptedblock' for all runs after first
      const XORBlock = await encryptionManager.XORCipher(decryptedBlock, previousBlock)

      //Appends decrypted block to result
      result.set(XORBlock, i)
      previousBlock = currentBlock;
    } 

    //Unpads result with PCKS#7 padding
    const unpaddedResult = await encryptionManager.unpadUint8Array(result);

    return unpaddedResult.buffer;

  }

}

export const encryptionManager = new EncryptionManager()



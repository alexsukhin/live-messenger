
export function openDatabase() {
    //Creates an IndexedDB database
    const request = indexedDB.open("RSAPrivateKeys", 1)
    
    //Sets up database structure
    request.onupgradeneeded = (event) => {
        const db = event.target.result;
        db.createObjectStore("Key", {keyPath: "userID"})
    }
    
    request.onsuccess = (event) => {
        const db = event.target.result;
    };
    
    request.onerror = (event) =>     {
        console.error("Error opening IndexedDB:", event.target.error);
    };

    return request;
}

export function saveKey(RSAPrivateKey, userID, db) {
    //Accesses Key storage
    const transaction = db.transaction(["Key"], "readwrite")
    const objStore = transaction.objectStore("Key")

    const key = {
        userID : userID,
        RSAPrivateKey: RSAPrivateKey
    };

    //Adds data to object store
    const addRequest = objStore.add(key)

    addRequest.onsuccess = (event) => {
        console.log("Private key saved successfully:", event.target.result);
    };

    addRequest.onerror = (event) => {
        console.error("Error saving private key:", event.target.error);
    };
}

export function getPrivateKey(userID, db) {
    //Accesses key storage
    const transaction = db.transaction(["Key"], "readonly")
    const objStore = transaction.objectStore("Key")

    //Gets key from userID
    const getRequest = objStore.get(userID)

    getRequest.onsuccess = (event) => {
        const privateKey = event.target.result
        console.log("Retrieved private key:", privateKey);
    };

    getRequest.onerror = (event) => {
        console.error("Error retrieving private key:", event.target.error);
    };
}
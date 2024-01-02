
//https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API/Using_IndexedDB

let globalDB = null;

export function openDatabase() {

    if (globalDB) {
        return Promise.resolve(globalDB);
    };

    return new Promise((resolve, reject) => {

            //Creates an IndexedDB database
            const request = indexedDB.open("RSAPrivateKeys", 1)
            
            //Sets up database structure
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                db.createObjectStore("Key", {keyPath: "userID"})
            };
            
            request.onsuccess = (event) => {
                const db = event.target.result;
                globalDB = db;
                resolve(db)
            };
            
            request.onerror = (event) =>     {
                console.error("Error opening IndexedDB:", event.target.error);
                reject(event.target.error)
            };


    })
}

export function saveKey(RSAPrivateKey, userID) {
    return new Promise((resolve, reject) => {

        const db = globalDB;

        if (!db) {
            console.error("Database not initialized.");
            return Promise.reject("Database not initialized.");
        }
    
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
            resolve(event.target.result)
        };
    
        addRequest.onerror = (event) => {
            console.error("Error saving private key:", event.target.error);
            reject(event.target.error);
        };

    })

}

export function getPrivateKey(userID) {

    return new Promise((resolve, reject) => {
        const db = globalDB;

        if (!db) {
            console.error("Database not initialized.");
            return Promise.reject("Database not initialized.");
        }


        //Accesses key storage
        const transaction = db.transaction(["Key"], "readonly")
        const objStore = transaction.objectStore("Key")

        //Gets key from userID
        const getRequest = objStore.get(userID)

        getRequest.onsuccess = (event) => {
            const privateKey = event.target.result
            console.log(getRequest)
            resolve(privateKey.RSAPrivateKey);
        };

        getRequest.onerror = (event) => {
            console.error("Error retrieving private key:", event.target.error);

            reject(event.target.error);
        };

    })
}
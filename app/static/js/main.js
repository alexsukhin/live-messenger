import {getConnectionID, getSessionID, getConversationID, getSenderID, getEncryptedAESKeys, decryptBase64Key, arrayBuffertoBase64, Base64toArrayBuffer, insertChatMessage, appendMessage, appendImage, appendFile} from "./functions.js";
import {encryptionManager} from "./encryption.js";
import {openDatabase, saveKey, getPrivateKey} from "./indexeddb.js";

let sessionSocket;
let AESKey;
let chatUserElements = [];
const db = openDatabase();

async function updateChatList() {

    //Gets list of all chat users into data variable via JSON
    const response = await fetch("/get-chat-users");
    const data = await response.json();

        //Loops through each chat user
        data.forEach(user => {

            //Gets user element which user clicked on
            let chatUserElement = chatUserElements.find(element => element.dataset.userId === user.userID);
            
            //Creates and pushes a chat user element via HTML if there is no pre-existing chat user element for user
            if (!chatUserElement) {
                chatUserElement = document.createElement("div");
                chatUserElement.className = "chat-user";
                chatUserElement.dataset.userId = user.userID;

                const usernameElement = document.createElement("h");
                const firstNameElement = document.createElement("h");   
                const lastNameElement = document.createElement("h");
                const notificationCounterElement = document.createElement("h2");
                const spaceElement = document.createTextNode(" ");
                const br = document.createElement("br");
                const hr = document.createElement("hr");
    
                usernameElement.textContent = user.username;
                firstNameElement.textContent = user.firstName;
                lastNameElement.textContent = user.lastName;

                if (user.notificationCounter !== 0) {
                    notificationCounterElement.textContent = user.notificationCounter;
                }
    
                chatUserElement.appendChild(usernameElement);
                chatUserElement.appendChild(notificationCounterElement);
                chatUserElement.appendChild(br);
                chatUserElement.appendChild(firstNameElement);
                chatUserElement.appendChild(spaceElement);
                chatUserElement.appendChild(lastNameElement);
                chatUserElement.appendChild(hr);


                chatUserElements.push(chatUserElement);
            }
                
        });

        // Determines the desired order based on the fetched data
        const desiredOrder = data.map(user => user.userID);
        const chatList = document.getElementById("chat-list");

        // Reorders chat user elements in chatList based on desired order
        desiredOrder.forEach(userId => {
            const chatUserElement = chatUserElements.find(element => element.dataset.userId === userId.toString());
            if (chatUserElement) {
                chatList.appendChild(chatUserElement);
            }
        });



};

async function updateUser(recipientID) {
    //Inserts into conversation and session databases when user selects a user to communicate with

    //Disconnects from current session websocket once user selects a different user to communicate with
    if (sessionSocket) {
        sessionSocket.disconnect();
        console.log('Websocket disconnected');
    }

    const senderID = await getSenderID();
    const connectionID = await getConnectionID(recipientID);

    //Checks if there is a connection between two users
    if (connectionID !== null) {

        const conversationCheckResponse = await fetch(`/check-conversation/${connectionID}`);
        const conversationCheckData = await conversationCheckResponse.json();

        //Generates AES key
        AESKey = await encryptionManager.generateAESKey();

        //Fetches sender public RSA key in preparation for encrypting sender AES Key
        const senderIDResponse = await fetch(`get-RSA-public-key/${senderID}`);
        const senderRSAPublicKey = await senderIDResponse.json().then(JSON.parse);

        //Fetches recipient public RSA key in preparation for encrypting recipient AES key
        const recipientIDResponse = await fetch(`get-RSA-public-key/${recipientID}`);
        const recipientRSAPublicKey = await recipientIDResponse.json().then(JSON.parse);

        //Encrypts AES keys and converts them to base64 strings
        const senderEncryptedAESKeyBuffer = await encryptionManager.encryptAESKey(AESKey, senderRSAPublicKey);
        const senderEncryptedAESKey = await arrayBuffertoBase64(senderEncryptedAESKeyBuffer);

        const recipientEncryptedAESKeyBuffer = await encryptionManager.encryptAESKey(AESKey, recipientRSAPublicKey);
        const recipientEncryptedAESKey = await arrayBuffertoBase64(recipientEncryptedAESKeyBuffer);

        //Checks if a conversation between two users has been created before
        if (!conversationCheckData) {

            //Inserts a conversation into database if there is not a conversation
            const insertConversationResponse = await fetch(`/insert-conversation/${connectionID}`);
            const insertConversationData = await insertConversationResponse.json();

            const conversationID = await getConversationID(connectionID);

            //Inserts a session into database and establishes websocket
            initiateSession(recipientID, conversationID, senderEncryptedAESKey, recipientEncryptedAESKey);


        } else {

            const conversationID = await getConversationID(connectionID);
            
            //Updates the conversation timestamp if there is already a conversation in database
            const updateConversationResponse = await fetch(`update-conversation/${conversationID}`)
            const updateConversationData = await updateConversationResponse.json();
            
            //Inserts a session into database and establishes websocket
            initiateSession(recipientID, conversationID, senderEncryptedAESKey, recipientEncryptedAESKey);



        }
    } else {
        console.log("Connection not found.");
    }

};

async function initiateSession(recipientID, conversationID, senderEncryptedAESKey, recipientEncryptedAESKey) {

    //Inserts a session into sessions database
    //Sends encryptedAESKeys as a POST request since they are base64 strings, otherwise too long
    const url = `/insert-session/${conversationID}`
    const data = {
        senderEncryptedAESKey : senderEncryptedAESKey,
        recipientEncryptedAESKey : recipientEncryptedAESKey
    }

    const insertSessionResponse = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }
    );

    const insertSessionData = await insertSessionResponse.json();

    const senderID = await getSenderID();

    //Connects and establishes a session websocket for current user
    sessionSocket = io.connect('http://127.0.0.1:5000');

    sessionSocket.on('connect', () => {
        //Establishes a web socket when user clicks on a user, resetting notification count
        console.log('WebSocket connection established');

        //Sends emit to socket.py to create and join a room
        sessionSocket.emit('join-room', recipientID);

        //Sends emit to socket.py to reset notifications
        sessionSocket.emit('reset-notification', recipientID);

    });



    sessionSocket.on('message', async (message) => {

        console.log("hello")

        const chatMessages = document.getElementById("chatbox-messages");
        //Gets dictionary of encrypted AES keys
        const base64EncryptedAESKeys = await getEncryptedAESKeys(message.sessionID);

        if (message.senderID == senderID) {

            //Gets sender encrypted AES key from dictionary and decrypts AES key
            const base64EncryptedAESKey = await base64EncryptedAESKeys.senderEncryptedAESKey
            const AESKey = await decryptBase64Key(senderID, base64EncryptedAESKey)

            appendMessage(message, senderID, chatMessages, AESKey);

        } else if (message.senderID == recipientID) {

            //Gets recipient encrypted AES key from dictionary and decrypts AES key
            const base64EncryptedAESKey = await base64EncryptedAESKeys.recipientEncryptedAESKey
            const AESKey = await decryptBase64Key(senderID, base64EncryptedAESKey)
    
            appendMessage(message, senderID, chatMessages, AESKey);

        }
    
    })



    sessionSocket.on('file', async (file) => {

        const chatMessages = document.getElementById("chatbox-messages");
        //Gets dictionary of encrypted AES keys
        const base64EncryptedAESKeys = await getEncryptedAESKeys(file.sessionID);

        if (file.senderID == senderID) {
            //Gets sender encrypted AES key from dictionary and decrypts AES key
            const base64EncryptedAESKey = await base64EncryptedAESKeys.senderEncryptedAESKey
            const AESKey = await decryptBase64Key(senderID, base64EncryptedAESKey)
            
            processMessage(AESKey);

        } else if (file.senderID == recipientID) {
            //Gets recipient encrypted AES key from dictionary and decrypts AES key
            const base64EncryptedAESKey = await base64EncryptedAESKeys.recipientEncryptedAESKey
            const AESKey = await decryptBase64Key(senderID, base64EncryptedAESKey)

            processMessage(AESKey);

        }

        async function processMessage(AESKey) {
            if (file.dataFormat == "text/plain" || file.dataFormat == "application/pdf") {
                appendFile(file, senderID, chatMessages, AESKey)
                
            } else if (file.dataFormat == "image/png" || file.dataFormat == "image/jpeg") {
                appendImage(file, senderID, chatMessages, AESKey)
        
            }

        }

    })



    sessionSocket.on('reset-notification', () => {

        //Gets user element which user clicked on
        let chatUserElement = chatUserElements.find(element => element.dataset.userId === recipientID);

        //Gets notification element from current chat user element
        const notificationCounterElement = chatUserElement.querySelector("h2");

        //Sets text content to an empty string, representing '0' i.e no notifications
        notificationCounterElement.textContent = "";

    })
    
};

document.getElementById("message-form").addEventListener("submit", async event => {
    event.preventDefault();

    const chatbox = document.getElementById("chatbox-user");
    const messageInput = document.getElementById("message");
    const plaintext = messageInput.value;

    const recipientID = chatbox.dataset.recipientId;    

    const connectionID = await getConnectionID(recipientID);
    const conversationID = await getConversationID(connectionID);
    const sessionID = await getSessionID(conversationID);

    const dataFormat = "text/short";

    //Resets message box to no text once user sends a message
    messageInput.value = "";

    //Randomly generates IV
    const IV = crypto.getRandomValues(new Uint8Array(16));

    //Encrypts plaintext with global AES key
    const bufferEncryptedContent = await encryptionManager.encryptData(plaintext, AESKey, IV);

    //Converts data and IV into base64 strings
    const base64EncryptedContent = await arrayBuffertoBase64(bufferEncryptedContent);
    const base64IV = await arrayBuffertoBase64(IV);

    //Emits message to flask server
    sessionSocket.emit('message', sessionID, recipientID, base64EncryptedContent, dataFormat, base64IV);

    //Increments notification on recipients side by one
    sessionSocket.emit('increment-notification', recipientID);

});

document.getElementById("file-upload").addEventListener("change", async event => {
    event.preventDefault()

    const chatbox = document.getElementById("chatbox-user");
    const fileInput = document.getElementById("file-input");
    const file = fileInput.files[0];
    const fileName = file.name;

    const recipientID = chatbox.dataset.recipientId;

    const connectionID = await getConnectionID(recipientID);
    const conversationID = await getConversationID(connectionID);
    const sessionID = await getSessionID(conversationID);

    
    //Randomly generates IV and converts to base64 string
    const IV = crypto.getRandomValues(new Uint8Array(16));
    const base64IV = await arrayBuffertoBase64(IV);

    const dataFormat = file.type;
    const acceptedFormat = ["text/plain", "application/pdf", "image/png", "image/jpeg"];

    const reader = new FileReader();

    reader.onload = async (data) => {
        const fileData = data.target.result;
        const encryptedFileData = await encryptionManager.encryptFile(fileData, AESKey, IV);

        //Emits encrypted rray buffer of bytes to python server
        sessionSocket.emit('file', sessionID, recipientID, encryptedFileData, fileName, dataFormat, base64IV);

        
    }

    if (acceptedFormat.includes(dataFormat)) {
        console.log("Accepted");
        //If file format is an accepted format, emits file to server as an array buffer
        reader.readAsArrayBuffer(file);
    } else {
        console.log("Not accepted");
    }

    sessionSocket.emit('increment-notification', recipientID);



});

document.addEventListener("DOMContentLoaded", async () => {

    //Disconnects user from websocket if they refresh the page or go to a different page
    document.addEventListener("beforeunload", () => {
        if (sessionSocket) {
            sessionSocket.disconnect();
        }
    })

    const senderID = await getSenderID();

    const idResponse = await fetch(`get-RSA-public-key/${senderID}`);
    const RSAPublicKey = await idResponse.json();

    //This code below to generate RSA key pairs is run only once once a user creates their account
    //If RSAPublicKey is null, generate RSA keys
    if (RSAPublicKey == null) {

        //Gets key pair for RSA encryption
        const keyPair = await encryptionManager.generateRSAKeyPair();

        //Updates public RSA key in users database
        const insertRSAResponse = await fetch(`/update-RSA-public-key/${keyPair.publicKey}`);
        const insertResponseData = await insertRSAResponse.json();
        console.log(insertResponseData);

        //Inserts sender private RSA key in IndexedDB Database
        await saveKey(keyPair.privateKey, senderID)

        console.log("No public key");
    } else {
        console.log("Public key");
    }



    const chatList = document.getElementById("chat-list");
    const chatbox = document.getElementById("chatbox-user");
    const introduction = document.getElementById("introduction");

    chatList.addEventListener("click", async event => {

        const clickedUser = event.target.closest(".chat-user");

        const recipientID = clickedUser.dataset.userId;
        chatbox.dataset.recipientId = recipientID;
        
        //Inserts clicked user into conversation and session databases, establishes websocket and resets notifications
        await updateUser(recipientID);
        
        //Updates chat list on left of screen to correct order
        await updateChatList();

        //Resets colour when selecting a different user
        const chatUsers = chatList.querySelectorAll(".chat-user");
        chatUsers.forEach(user => {
            user.style.backgroundColor = "";
        });

        //Sets clicked user to a darker background colour
        clickedUser.style.backgroundColor = "#dde4e4";
    
        //Displays chatbox
        introduction.style.display = "none";
        chatbox.style.display = "block";
 
        //Clears previous chat messages in HTML
        const chatMessages = document.getElementById("chatbox-messages");
        chatMessages.innerHTML = "";

        //Creates map for storing previous AES keys, speeding up message retrieval
        const AESKeyDict = new Map();

        //Gets list of all chat messages in a data variable via JSON
        const response = await fetch(`/get-chat-messages/${recipientID}`);
        const data = await response.json();

        //Loops through all messages synchronously, decrypting them and pushing them to HTML, outputting to user's screen
        for (const message of data) {

            const idResponse = await fetch(`get-encrypted-AES-key/${message.sessionID}`);
            const base64EncryptedAESKeys = await idResponse.json();

            let base64EncryptedAESKey;

            if (message.senderID == senderID) {

                base64EncryptedAESKey = base64EncryptedAESKeys.senderEncryptedAESKey;
    
            } else if (message.senderID == recipientID) {

                base64EncryptedAESKey = base64EncryptedAESKeys.recipientEncryptedAESKey;

            };

            //If program has found previous stored encrypted AES key, gets decrypted AES key from map
            //preventing program from re-decrypting already decrypted AES key
            if (AESKeyDict.has(base64EncryptedAESKey)) {
                const AESKey = AESKeyDict.get(base64EncryptedAESKey);

                processMessage(AESKey, message);
            } else {
                //Gets RSA Private key from IndexedDB Database
                const RSAPrivateKey = await getPrivateKey(senderID);

                const encryptedAESKey = await Base64toArrayBuffer(base64EncryptedAESKey);
                
                const AESKey = await encryptionManager.decryptAESKey(encryptedAESKey.buffer, RSAPrivateKey);

                //Pushes decrypted AES key to map
                AESKeyDict.set(base64EncryptedAESKey, AESKey);

                processMessage(AESKey, message);

            }

            async function processMessage(AESKey, message) {

                if (message.dataFormat == "text/short") {
    
                        appendMessage(message, senderID, chatMessages, AESKey);
    
                } else if (message.dataFormat == "text/plain" || message.dataFormat == "application/pdf") {
    
                        appendFile(message, senderID, chatMessages, AESKey);
    
                } else if (message.dataFormat == "image/png" || message.dataFormat == "image/jpeg") {
    
                        appendImage(message, senderID, chatMessages, AESKey);
    
                } else {
                    console.log("Invalid file type");
                }
    
    
            }
            
        };

    
    });
    
    document.getElementById("add-user-button").addEventListener("click", () => {
        updateChatList();
    });

    
    updateChatList();

});
import {getConnectionID, getSessionID, getConversationID, updateChatList, appendMessage, appendImage, appendFile} from "./functions.js";

let sessionSocket;

async function initiateSession(conversationID, encryptedAESKey) {
    const insertSessionResponse = await fetch(`/insert-session/${conversationID}/${encryptedAESKey}`);
    const insertSessionData = await insertSessionResponse.json();
    console.log("Session Data:", insertSessionData);


    //Connects and establishes a session websocket for current user
    sessionSocket = io.connect('http://127.0.0.1:5000');

    sessionSocket.on('connect', () => {
        console.log('WebSocket connection established');
    });


    sessionSocket.on('message', async (message) => {
        console.log("Received message:", message);
        
        const idResponse = await fetch(`get-sender-id`);
        const senderID = await idResponse.json();

        const chatMessages = document.getElementById("chatbox-messages");

        appendMessage(message, senderID, chatMessages)

        
    })

    sessionSocket.on('file', async (file) => {
        console.log("Received file:", file);

        const idResponse = await fetch(`get-sender-id`);
        const senderID = await idResponse.json();

        const chatMessages = document.getElementById("chatbox-messages");
        
            
        if (file.dataFormat == "text/plain" || file.dataFormat == "application/pdf") {

            const decodedText = atob(file.encryptedContent)

            appendFile(file, senderID, decodedText, chatMessages)


        } else if (file.dataFormat == "image/png" || file.dataFormat == "image/jpeg") {
            
            const dataURL = `data:${file.dataFormat};base64,${file.encryptedContent}`

            appendImage(file, senderID, dataURL, chatMessages)

        }

        

    })


};

async function updateUser(recipientID) {
    //Inserts into conversation and session databases when user selects a user to communicate with

    //Disconnects from current session websocket once user selects a different user to communicate with
    if (sessionSocket) {
        sessionSocket.disconnect()
        console.log('Websocket disconnected')
    }

    const encryptedAESKey = "test";

    const connectionID = await getConnectionID(recipientID);

    //Checks if there is a connection between two users
    if (connectionID !== null) {

        const conversationCheckResponse = await fetch(`/check-conversation/${connectionID}`);
        const conversationCheckData = await conversationCheckResponse.json();



        //Checks if a conversation between two users has been created before
        if (!conversationCheckData) {

            //Inserts a conversation into database if there is not a conversation
            const insertConversationResponse = await fetch(`/insert-conversation/${connectionID}`);
            const insertConversationData = await insertConversationResponse.json();
            console.log("Conversation Data:", insertConversationData)

            const conversationID = await getConversationID(connectionID)

            //Inserts a session into database and establishes websocket
            initiateSession(conversationID, encryptedAESKey);


        } else {

            const conversationID = await getConversationID(connectionID)
            
            //Updates the conversation timestamp if there is already a conversation in database
            const updateConversationResponse = await fetch(`update-conversation/${conversationID}`)
            const updateConversationData = await updateConversationResponse.json();
            console.log("Update Data:", updateConversationData)
            
            //Inserts a session into database and establishes websocket
            initiateSession(conversationID, encryptedAESKey)


        }
    } else {
        console.log("Connection not found.");
    }
}

document.getElementById("message-form").addEventListener("submit", async event => {
    event.preventDefault();

    const chatbox = document.getElementById("chatbox-user");
    const messageInput = document.getElementById("message");
    const encryptedContent = messageInput.value;

    const recipientID = chatbox.dataset.recipientId;

    const connectionID = await getConnectionID(recipientID);
    const conversationID = await getConversationID(connectionID);
    const sessionID = await getSessionID(conversationID);

    const dataFormat = "text/short"

    messageInput.value = "";

    //Emits message to flask server
    sessionSocket.emit('message', sessionID, recipientID, encryptedContent, dataFormat);


});

document.getElementById("file-upload").addEventListener("change", async event => {
    event.preventDefault()

    const chatbox = document.getElementById("chatbox-user");
    const fileInput = document.getElementById("file-input");
    const file = fileInput.files[0];
    
    //Splits true file name into two parts e.g. image.png -> ["image", "png"]
    const fileName = file.name

    const recipientID = chatbox.dataset.recipientId;

    const connectionID = await getConnectionID(recipientID);
    const conversationID = await getConversationID(connectionID);
    const sessionID = await getSessionID(conversationID);

    const IV = "test"
    const dataFormat = file.type;
    const acceptedFormat = ["text/plain", "application/pdf", "image/png", "image/jpeg"]

    const reader = new FileReader();

    reader.onload = (data) => {
        const fileData = data.target.result

        sessionSocket.emit('file', sessionID, recipientID, fileData, fileName, dataFormat, IV);
    }

    if (acceptedFormat.includes(dataFormat)) {
        console.log("Accepted")
        reader.readAsArrayBuffer(file);
    } else {
        console.log("Not accepted")
        //possible gui response
    }

});


document.addEventListener("DOMContentLoaded", () => {

    const chatList = document.getElementById("chat-list");
    const chatbox = document.getElementById("chatbox-user");
    const introduction = document.getElementById("introduction");

    chatList.addEventListener("click", async event => {

        const clickedUser = event.target.closest(".chat-user");

        const recipientID = clickedUser.dataset.userId;
        chatbox.dataset.recipientId = recipientID;
        
        await updateUser(recipientID);
        
        await updateChatList();


        //Resets colour when selecting a different user
        const chatUsers = chatList.querySelectorAll(".chat-user");
        chatUsers.forEach(user => {
            user.style.backgroundColor = "";
        });
    
        clickedUser.style.backgroundColor = "#dde4e4";
    
        introduction.style.display = "none";
        chatbox.style.display = "block";

        const idResponse = await fetch(`get-sender-id`);
        const senderID = await idResponse.json();
 
        //Clears previous chat messages in HTML
        const chatMessages = document.getElementById("chatbox-messages");

        chatMessages.innerHTML = ""

        //Gets list of all chat messages in a data variable via JSON
        const response = await fetch(`/get-chat-messages/${recipientID}`);
        const data = await response.json();

        //decrypt all messages in future
        
        //Loops through all messages and pushes it to messages HTML, outputting to user's screen
        data.forEach(message => {

            if (message.dataFormat == "text/short") {

                appendMessage(message, senderID, chatMessages)
                
            } else if (message.dataFormat == "text/plain" || message.dataFormat == "application/pdf") {

                const decodedText = atob(message.encryptedContent)

                appendFile(message, senderID, decodedText, chatMessages)

            } else if (message.dataFormat == "image/png" || message.dataFormat == "image/jpeg") {
                
                const dataURL = `data:${message.dataFormat};base64,${message.encryptedContent}`

                appendImage(message, senderID, dataURL, chatMessages)

            } else {
                console.log("Invalid file type")
            }
        });
    
    });
    
    document.getElementById("add-user-button").addEventListener("click", () => {
        updateChatList();
    });

    
    updateChatList();

});
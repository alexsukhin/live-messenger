let chatUserElements = [];
let sessionSocket;

async function getConnectionID(recipientID) {
    //Gets connection ID and returns as a JSON response
    const connectionResponse = await fetch(`/get-connection-id/${recipientID}`);
    const connectionData = await connectionResponse.json();
    return connectionData[0];
}

async function getSessionID(conversationID) {
    //Gets session ID and returns as a JSON response
    const sessionResponse = await fetch(`/get-latest-session-id/${conversationID}`)
    const sessionData = await sessionResponse.json()
    return sessionData[0]
}

async function getConversationID(connectionID) {
    //Gets conversation ID and returns as a JSON response
    const conversationResponse = await fetch(`/get-conversation-id/${connectionID}`);
    const conversationData = await conversationResponse.json();
    return conversationData[0];
}

async function updateChatList() {

    //Gets list of all chat users into data variable via JSON
    const response = await fetch("/get-chat-users");
    const data = await response.json();

        //Loops through each chat user
        data.forEach(user => {
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
    
                chatUserElement.appendChild(usernameElement);
                chatUserElement.appendChild(notificationCounterElement);
                chatUserElement.appendChild(br);
                chatUserElement.appendChild(firstNameElement);
                chatUserElement.appendChild(spaceElement);
                chatUserElement.appendChild(lastNameElement);
                chatUserElement.appendChild(hr);


                chatUserElements.push(chatUserElement);
            }
                
            if (user.notificationCounter !== 0) {
                notificationCounterElement.textContent = user.notificationCounter;
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



}

async function initiateSession(conversationID, encryptedAESKey, socketID) {
    const insertSessionResponse = await fetch(`/insert-session/${conversationID}/${encryptedAESKey}/${socketID}`);
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

        if (message.senderID == senderID) {
            senderMessage = document.createElement("div");
            senderMessage.className = "sender-message";
            senderMessage.textContent = message.encryptedContent;

            //If pre-existing messages, inserts message at start of HTML code, else pushes message to HTML
            //Ensures messages are not in reverse-order
            if (chatMessages.firstChild) {
                chatMessages.insertBefore(senderMessage, chatMessages.firstChild);
            }
            else {
                chatMessages.appendChild(senderMessage, chatMessages.firstChild);
            }
        }

        else if (message.senderID == recipientID) {
            recipientMessage = document.createElement("div");
            recipientMessage.className = "recipient-message";
            recipientMessage.textContent = message.encryptedContent;

            //If pre-existing messages, inserts message at start of HTML code, else pushes message to HTML
            //Ensures messages are not in reverse-order
            if (chatMessages.firstChild) {
                chatMessages.insertBefore(recipientMessage, chatMessages.firstChild);
            }
            else {
                chatMessages.appendChild(recipientMessage, chatMessages.firstChild);
            }
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
    const socketID = "test";

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
            initiateSession(conversationID, encryptedAESKey, socketID);


        } else {

            const conversationID = await getConversationID(connectionID)
            
            //Updates the conversation timestamp if there is already a conversation in database
            const updateConversationResponse = await fetch(`update-conversation/${conversationID}`)
            const updateConversationData = await updateConversationResponse.json();
            console.log("Update Data:", updateConversationData)
            
            //Inserts a session into database and establishes websocket
            initiateSession(conversationID, encryptedAESKey, socketID)


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

    const IV = "test"
    const dataFormat = "text"

    messageInput.value = "";

    //Emits message to flask server
    sessionSocket.emit('message', sessionID, recipientID, encryptedContent, IV, dataFormat);


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

        data.reverse();
        
        //Loops through all messages and pushes it to messages HTML, outputting to user's screen
        data.forEach(message => {

            if (message.senderID == senderID) {
                senderMessage = document.createElement("div");
                senderMessage.className = "sender-message";
                senderMessage.textContent = message.encryptedContent;
                chatMessages.appendChild(senderMessage);
            }

            else if (message.senderID == recipientID) {
                recipientMessage = document.createElement("div");
                recipientMessage.className = "recipient-message";
                recipientMessage.textContent = message.encryptedContent;
                chatMessages.appendChild(recipientMessage);
            }
        });
    
    });
    
    document.getElementById("add-user-button").addEventListener("click", () => {
        updateChatList();
    });

    
    updateChatList();

});
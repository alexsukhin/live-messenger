let chatUserElements = [];

async function updateChatList() {

    const response = await fetch("/get-chat-users");
    const data = await response.json();

            
        data.forEach(user => {
            let chatUserElement = chatUserElements.find(element => element.dataset.userId === user.userID);

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

        // Determine the desired order based on the fetched data
        const desiredOrder = data.map(user => user.userID);
        const chatList = document.getElementById("chat-list");

        // Reorder chat user elements in chatList based on desired order
        desiredOrder.forEach(userId => {
            const chatUserElement = chatUserElements.find(element => element.dataset.userId === userId.toString());
            if (chatUserElement) {
                chatList.appendChild(chatUserElement);
            }
        });



}

async function updateUser(senderID, recipientID) {
    // Inserts into conversation, session databases

    const encryptedAESKey = "test";
    const socketID = "test";

    async function getConversationID(connectionID) {
        const conversationResponse = await fetch(`/get-conversation-id/${connectionID}`);
        const conversationData = await conversationResponse.json();
        return conversationData[0];
    }

    const connectionResponse = await fetch(`/get-connection-id/${senderID}/${recipientID}`);
    const connectionData = await connectionResponse.json();
    const connectionID = connectionData[0]

    if (connectionData.connectionID !== null) {

        const conversationCheckResponse = await fetch(`/check-conversation/${connectionID}`);
        const conversationCheckData = await conversationCheckResponse.json();

        if (!conversationCheckData) {

            
            const insertConversationResponse = await fetch(`/insert-conversation/${connectionID}`);
            const insertConversationData = await insertConversationResponse.json();

            console.log("Conversation Data:", insertConversationData)

            const conversationID = await getConversationID(connectionID)

            const insertSessionResponse = await fetch(`/insert-session/${conversationID}/${encryptedAESKey}/${socketID}/${senderID}`);
            const insertSessionData = await insertSessionResponse.json();
            
    
            console.log("Session Data:", insertSessionData);

        } else {

            const conversationID = await getConversationID(connectionID)

            const updateConversationResponse = await fetch(`update-conversation/${conversationID}`)
            const updateConversationData = await updateConversationResponse.json();

            console.log("Update Data:", updateConversationData)

            const insertSessionResponse = await fetch(`/insert-session/${conversationID}/${encryptedAESKey}/${socketID}/${senderID}`);
            const insertSessionData = await insertSessionResponse.json();

            console.log("Session Data:", insertSessionData);

        }
    } else {
        console.log("Connection not found.");
    }
    
}

document.addEventListener("DOMContentLoaded", () => {

    const chatList = document.getElementById("chat-list");
    const chatbox = document.getElementById("chatbox-user");
    const introduction = document.getElementById("introduction");

    chatList.addEventListener("click", async event => {

        const clickedUser = event.target.closest(".chat-user");

        const idResponse = await fetch(`/get-sender-id`);
        const senderID = await idResponse.json();

        const recipientID = clickedUser.dataset.userId;
        console.log(recipientID)
        //chatbox.dataset.recipientId = recipientID; - use if i need this later

        //Sends recipientID directly into views.py
        await fetch(`/send-recipient-id/${recipientID}`, {method: "POST"});

        await updateUser(senderID, recipientID)
        
        await updateChatList();
        
        const chatUsers = chatList.querySelectorAll(".chat-user");
        chatUsers.forEach(user => {
            user.style.backgroundColor = "";
        });
    
        clickedUser.style.backgroundColor = "#dde4e4";
    
        introduction.style.display = "none";
        chatbox.style.display = "block";
    
    });
    
    document.querySelector("#add-user-button").addEventListener("click", () => {
        updateChatList();
    });

    
    updateChatList();

});

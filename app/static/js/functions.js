let chatUserElements = [];

export async function getConnectionID(recipientID) {
    //Gets connection ID and returns as a JSON response
    const connectionResponse = await fetch(`/get-connection-id/${recipientID}`);
    const connectionData = await connectionResponse.json();
    return connectionData[0];
}

export async function getSessionID(conversationID) {
    //Gets session ID and returns as a JSON response
    const sessionResponse = await fetch(`/get-latest-session-id/${conversationID}`)
    const sessionData = await sessionResponse.json()
    return sessionData[0]
}

export async function getConversationID(connectionID) {
    //Gets conversation ID and returns as a JSON response
    const conversationResponse = await fetch(`/get-conversation-id/${connectionID}`);
    const conversationData = await conversationResponse.json();
    return conversationData[0];
}

export function appendMessage(message, senderID, chatMessages) {
    if (message.senderID == senderID) {
        const senderMessage = document.createElement("div");
        senderMessage.className = "sender-message";
        senderMessage.textContent = message.encryptedContent;

        //If pre-existing messages, inserts message at start of HTML code, else pushes message to HTML
        //Ensures files are not in reverse-order
        if (chatMessages.firstChild) {
            chatMessages.insertBefore(senderMessage, chatMessages.firstChild);
        }
        else {
            chatMessages.appendChild(senderMessage, chatMessages.firstChild);
        }
    }

    else if (message.recipientID == senderID) {
        const recipientMessage = document.createElement("div");
        recipientMessage.className = "recipient-message";
        recipientMessage.textContent = message.encryptedContent;

        //If pre-existing messages, inserts message at start of HTML code, else pushes message to HTML
        //Ensures files are not in reverse-order
        if (chatMessages.firstChild) {
            chatMessages.insertBefore(recipientMessage, chatMessages.firstChild);
        }
        else {
            chatMessages.appendChild(recipientMessage, chatMessages.firstChild);
        }
    }
}

export function appendImage(file, senderID, dataURL, chatMessages) {
    if (file.senderID == senderID) {
        const senderImage = document.createElement("img");
        senderImage.className = "sender-file"
        senderImage.src = dataURL;

        //If pre-existing messages, inserts message at start of HTML code, else pushes message to HTML
        //Ensures files are not in reverse-order
        if (chatMessages.firstChild) {
            chatMessages.insertBefore(senderImage, chatMessages.firstChild);
        }
        else {
            chatMessages.appendChild(senderImage, chatMessages.firstChild);
        }

    
    } else if (file.recipientID == senderID) {
        const recipientImage = document.createElement("img");
        recipientImage.className = "recipient-file"
        recipientImage.src = dataURL;

        //If pre-existing messages, inserts message at start of HTML code, else pushes message to HTML
        //Ensures messages are not in reverse-order
        if (chatMessages.firstChild) {
            chatMessages.insertBefore(recipientImage, chatMessages.firstChild);
        }
        else {
            chatMessages.appendChild(recipientImage, chatMessages.firstChild);
        }
    }
}

export function appendFile(file, senderID, content, chatMessages) {

    let blob;

    //https://stackoverflow.com/questions/21797299/convert-base64-string-to-arraybuffer
    //Converts base64 string into 8 bit array of bytes in order to output PDF files correctly
    const bytes = new Uint8Array(content.length);
    for (let i = 0; i < content.length; i++) {
        bytes[i] = content.charCodeAt(i)
    }
    
    if (file.senderID == senderID) {

        const filePath = file.filePath
        const fileName = (filePath.split("%"))[1];

        if (file.dataFormat == "text/plain") {
            blob = new Blob([content], {type: "text/plain"});
        } else if (file.dataFormat == "application/pdf") {
            blob = new Blob([bytes], {type: "application/pdf"});
        }   

        const senderLink = document.createElement("a");
    
        senderLink.className = "sender-message"
        senderLink.href = window.URL.createObjectURL(blob);
        senderLink.download = fileName;
        senderLink.innerText = fileName;

        if (chatMessages.firstChild) {
            chatMessages.insertBefore(senderLink, chatMessages.firstChild);
        }
        else {
            chatMessages.appendChild(senderLink, chatMessages.firstChild);
        }

    } else if (file.recipientID == senderID) {

        const filePath = file.filePath
        const fileName = (filePath.split("%"))[1];
    
        if (file.dataFormat == "text/plain") {
            blob = new Blob([content], {type: "text/plain"});
        } else if (file.dataFormat == "application/pdf") {
            blob = new Blob([bytes], {type: "application/pdf"});
        }   

        const recipientLink = document.createElement("a");
    
        recipientLink.className = "recipient-message"
        recipientLink.href = window.URL.createObjectURL(blob);
        recipientLink.download = fileName;
        recipientLink.innerText = fileName;

        if (chatMessages.firstChild) {
            chatMessages.insertBefore(recipientLink, chatMessages.firstChild);
        }
        else {
            chatMessages.appendChild(recipientLink, chatMessages.firstChild);
        }

    }

}

export async function updateChatList() {

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


export async function getConnectionID(recipientID) {
    //Gets connection ID and returns as a JSON response
    const connectionResponse = await fetch(`/get-connection-id/${recipientID}`);
    const connectionData = await connectionResponse.json();
    return connectionData[0];
};

export async function getSessionID(conversationID) {
    //Gets session ID and returns as a JSON response
    const sessionResponse = await fetch(`/get-latest-session-id/${conversationID}`)
    const sessionData = await sessionResponse.json()
    return sessionData[0]
};

export async function getConversationID(connectionID) {
    //Gets conversation ID and returns as a JSON response
    const conversationResponse = await fetch(`/get-conversation-id/${connectionID}`);
    const conversationData = await conversationResponse.json();
    return conversationData[0];
};

export async function getSenderID() {
    //Gets sender ID and returns as a JSON response
    const idResponse = await fetch(`get-sender-id`);
    const senderID = await idResponse.json();
    return senderID
};

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
};

export function appendImage(file, senderID, chatMessages) {

    //Assigns correct URL format to output images to HTML in base64
    const dataURL = `data:${file.dataFormat};base64,${file.encryptedContent}`

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
};

export function appendFile(file, senderID, chatMessages) {

    //Splits file path from path to file on server to file name user originally proposed, e.g. 'image.png'
    const filePath = file.filePath
    const fileName = (filePath.split("%"))[1];

    //Decodes base64 string to plaintext
    const plaintext = atob(file.encryptedContent)

    //https://stackoverflow.com/questions/21797299/convert-base64-string-to-arraybuffer
    //Converts plaintext into 8 bit array of bytes in order to output PDF files correctly
    const bytes = new Uint8Array(plaintext.length);
    for (let i = 0; i < plaintext.length; i++) {
        bytes[i] = plaintext.charCodeAt(i)
    }

    let blob;

    //Assigns plaintext or bytes to blob depending on file format
    if (file.dataFormat == "text/plain") {
        blob = new Blob([plaintext], {type: "text/plain"});
    } else if (file.dataFormat == "application/pdf") {
        blob = new Blob([bytes], {type: "application/pdf"});
    }   
    
    if (file.senderID == senderID) {

        const senderLink = document.createElement("a");
    
        senderLink.className = "sender-message"
        senderLink.href = window.URL.createObjectURL(blob);
        senderLink.download = fileName;
        senderLink.textContent = fileName;

        //If pre-existing messages, inserts message at start of HTML code, else pushes message to HTML
        //Ensures files are not in reverse-order
        if (chatMessages.firstChild) {
            chatMessages.insertBefore(senderLink, chatMessages.firstChild);
        }
        else {
            chatMessages.appendChild(senderLink, chatMessages.firstChild);
        }

    } else if (file.recipientID == senderID) {

        const recipientLink = document.createElement("a");
    
        recipientLink.className = "recipient-message"
        recipientLink.href = window.URL.createObjectURL(blob);
        recipientLink.download = fileName;
        recipientLink.textContent = fileName;

        //If pre-existing messages, inserts message at start of HTML code, else pushes message to HTML
        //Ensures files are not in reverse-order
        if (chatMessages.firstChild) {
            chatMessages.insertBefore(recipientLink, chatMessages.firstChild);
        }
        else {
            chatMessages.appendChild(recipientLink, chatMessages.firstChild);
        }

    }

};
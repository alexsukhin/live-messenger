
function updateChatList() {

    fetch('/get-chat-users')
        .then(response => response.json())
        .then(data => {

            const chatList = document.getElementById('chat-list');

            chatList.innerHTML = '';

            data.forEach(user => {
                const chatUserElement = document.createElement('div');
                chatUserElement.className = 'chat-user';
                chatUserElement.dataset.userId = user.userID;

                const usernameElement = document.createElement('h');
                const firstNameElement = document.createElement('h');   
                const lastNameElement = document.createElement('h');
                const spaceElement = document.createTextNode(' ')
                const br = document.createElement('br');
                const hr = document.createElement('hr');

                usernameElement.textContent = user.username;
                firstNameElement.textContent = user.firstName;
                lastNameElement.textContent = user.lastName;


                chatUserElement.appendChild(usernameElement);
                chatUserElement.appendChild(br);
                chatUserElement.appendChild(firstNameElement);
                chatUserElement.appendChild(spaceElement);
                chatUserElement.appendChild(lastNameElement);
                chatUserElement.appendChild(hr);
                chatList.appendChild(chatUserElement);
            });

        })
}


document.addEventListener('DOMContentLoaded', () => {
    updateChatList();

    document.querySelector("#add-user-button").addEventListener("click", () => {
        updateChatList();
    });
});


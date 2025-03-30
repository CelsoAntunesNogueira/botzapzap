document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.querySelector(".chat-footer input");
    const sendButton = document.querySelector(".chat-footer button");
    const chatWindow = document.querySelector(".chat-window");
    const contacts = document.querySelectorAll(".contact");
    const chatHeader = document.querySelector(".chat-header h3");

    let activeContact = "Bot Zap Zap"; // Nome do contato ativo
    chatHeader.textContent = activeContact;

    // Enviar mensagem ao clicar no botão
    sendButton.addEventListener("click", sendMessage);

    // Enviar mensagem ao pressionar Enter
    inputField.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // Alternar entre contatos
    contacts.forEach(contact => {
        contact.addEventListener("click", function () {
            activeContact = this.textContent;
            //chatHeader.textContent = activeContact;
            chatWindow.innerHTML = ""; // Limpa o chat ao mudar de contato
        });
    });

    function sendMessage() {
        const messageText = inputField.value.trim();
        if (messageText === "") return;
        
        // Criar elemento de mensagem enviada
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", "sent");
        messageElement.textContent = messageText;
        chatWindow.appendChild(messageElement);

        inputField.value = "";
        scrollToBottom();

        // Enviar para o servidor (backend Flask)
    const BASE_URL = window.location.hostname === "https://botzapzap-pm0m.onrender.com";    
    fetch(`${BASE_URL}/webhook`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ Body: messageText })
    })
    .then(response => response.text())
    .then(text => {
        // Exibe a resposta do bot na tela
        const data = JSON.parse(text);
        const responseElement = document.createElement("div");
        responseElement.classList.add("message", "received");
        responseElement.textContent = data.response;
        chatWindow.appendChild(responseElement);
        scrollToBottom();
    } catch (error){
         console.error("Erro no JSON",error);
    })
    .catch(error => console.error('Error:', error));
        
    }

    function scrollToBottom() {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});

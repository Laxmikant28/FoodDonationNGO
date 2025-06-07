// static/js/chatbot.js

document.addEventListener('DOMContentLoaded', function() {
    const chatbotIcon = document.getElementById('chatbot-icon');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotSend = document.getElementById('chatbot-send');

    chatbotWindow.style.display = 'none';
    // Toggle chatbot window visibility
    chatbotIcon.addEventListener('click', function() {
        const isHidden = chatbotWindow.style.display === 'none' || chatbotWindow.style.display === '';
        chatbotWindow.style.display = isHidden ? 'flex' : 'none'; // Use 'flex' as per CSS display style
        if (isHidden) {
            // Optional: Scroll to bottom when opening
             chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }
    });

    // Function to add a message to the chat window
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(sender + '-message'); // 'user-message' or 'bot-message'
        messageElement.textContent = message;
        chatbotMessages.appendChild(messageElement);

        // Scroll to the latest message
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // Function to send message and get dummy response
    function sendMessage() {
        const message = chatbotInput.value.trim();
        if (message) {
            // Display user message immediately
            addMessage(message, 'user');
            chatbotInput.value = ''; // Clear the input field

            // --- Send message to Flask backend (using Fetch API) ---
            fetch('/send_message', { // This URL must match your Flask route
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message }) // Send message as JSON
            })
            .then(response => response.json()) // Parse the JSON response from Flask
            .then(data => {
                // Display the bot's dummy response
                addMessage(data.response, 'bot'); // Assuming Flask sends {'response': '...'}
            })
            .catch(error => {
                console.error('Error sending message:', error);
                addMessage("Sorry, something went wrong.", 'bot'); // Display an error message
            });
            // --- End of Flask backend communication ---

        }
    }

    // Send message on button click
    chatbotSend.addEventListener('click', sendMessage);

    // Send message on Enter key press in the input field
    chatbotInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form submission
            sendMessage();
        }
    });

    // Optional: Initial bot message when the page loads (already added in HTML)
    // addMessage("Hello! How can I help you today?", 'bot');
});
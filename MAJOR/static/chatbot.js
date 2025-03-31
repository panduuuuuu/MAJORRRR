document.addEventListener("DOMContentLoaded", function () {
    const chatbot = document.getElementById("chatbot");
    const chatbotButton = document.getElementById("chatbot-button");
    const closeChatbot = document.getElementById("close-chatbot");

    // Show the chatbox when the button is clicked
    chatbotButton.addEventListener("click", () => {
        chatbot.style.display = "flex"; // Expand the chatbox
        chatbotButton.style.display = "none"; // Hide the button
    });

    // Close the chatbox when the close button is clicked
    closeChatbot.addEventListener("click", () => {
        chatbot.style.display = "none"; // Collapse the chatbox
        chatbotButton.style.display = "flex"; // Show the button again
    });
});

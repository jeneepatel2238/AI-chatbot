function toggleChat() {
    const widget = document.getElementById("chat-widget");
    widget.style.display = widget.style.display === "none" ? "block" : "none";
}

function addMessage(sender, text) {
    const box = document.getElementById("chat-box");
    box.innerHTML += `<p><b>${sender}:</b> ${text}</p>`;
    box.scrollTop = box.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value;
    if (!message) return;

    addMessage("You", message);
    input.value = "";

    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    const data = await response.json();
    addMessage("Bot", data.reply);
}

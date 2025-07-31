// app.js (Improved Version)

// Constants
const MAX_HISTORY = 50;

const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("input-field");
const sendBtn = document.getElementById("send-btn");

// Utility to create timestamps
function formatTimestamp(date = new Date()) {
    return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}

// Add message to chat window, supports timestamp and ARIA live region
function addMessage(sender, text, timestamp = formatTimestamp()) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
    messageDiv.setAttribute("role", "listitem");

    // Message content
    const textSpan = document.createElement("span");
    textSpan.className = "message-text";
    textSpan.textContent = text;

    // Timestamp
    const timeSpan = document.createElement("span");
    timeSpan.className = "message-time";
    timeSpan.textContent = ` ${timestamp}`;

    messageDiv.appendChild(textSpan);
    messageDiv.appendChild(timeSpan);
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Load chat history from localStorage
function loadMemory() {
    try {
        const history = JSON.parse(localStorage.getItem("chat_history")) || [];
        if (!Array.isArray(history)) throw new Error("Invalid history format!");
        const limitedHistory = history.slice(-MAX_HISTORY);

        limitedHistory.forEach(entry => {
            if (entry.user && entry.bot) {
                addMessage("user", entry.user, entry.userTime || undefined);
                addMessage("bot", entry.bot, entry.botTime || undefined);
            }
        });
    } catch (e) {
        console.warn("Local history could not be read or is corrupted. Resetting.", e);
        localStorage.removeItem("chat_history");
    }
}

// Save new message pair to localStorage, including timestamps
function saveToMemory(userMsg, botReply) {
    try {
        let history = JSON.parse(localStorage.getItem("chat_history")) || [];
        if (!Array.isArray(history)) history = [];

        if (history.length >= MAX_HISTORY) {
            history.shift();
        }

        history.push({
            user: userMsg,
            bot: botReply,
            userTime: formatTimestamp(),
            botTime: formatTimestamp()
        });
        localStorage.setItem("chat_history", JSON.stringify(history));
    } catch (e) {
        console.warn("Could not save to local history:", e);
    }
}

// Display a loading indicator for bot response
function showLoading() {
    const loadingDiv = document.createElement("div");
    loadingDiv.classList.add("message", "bot-message", "loading-indicator");
    loadingDiv.setAttribute("role", "listitem");
    loadingDiv.textContent = "Yanıt bekleniyor...";
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return loadingDiv;
}

// Remove loading indicator
function removeLoading(loadingDiv) {
    if (loadingDiv && loadingDiv.parentNode) {
        loadingDiv.parentNode.removeChild(loadingDiv);
    }
}

// Send message to API and handle response
async function sendMessage() {
    const userMsg = inputField.value.trim();
    if (!userMsg) return;

    // Add user message and clear input
    addMessage("user", userMsg);
    inputField.value = "";
    inputField.disabled = true;
    sendBtn.disabled = true;

    const loadingDiv = showLoading();
    const t0 = performance.now();

    try {
        const response = await fetch("/api/v1/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ user_message: userMsg })
        });

        const data = await response.json();

        removeLoading(loadingDiv);

        // Basic sanitization: prevent XSS if bot replies could contain HTML
        const reply = document.createElement("div");
        reply.textContent = (data && typeof data.response === "string")
            ? data.response
            : "⚠️ Yanıt alınamadı.";

        addMessage("bot", reply.textContent);

        saveToMemory(userMsg, reply.textContent);

    } catch (error) {
        console.error("API request failed:", error);
        removeLoading(loadingDiv);
        addMessage("bot", "⚠️ Sunucuya ulaşılamadı.");
    }

    const t1 = performance.now();
    console.log(`Yanıt süresi: ${(t1 - t0).toFixed(2)} ms`);

    inputField.disabled = false;
    sendBtn.disabled = false;
    inputField.focus();
}

// Keyboard listener: Enter to send, Shift+Enter for newline
inputField.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Button listener
sendBtn.addEventListener("click", sendMessage);

// Load memory and focus input on page load
window.addEventListener("DOMContentLoaded", () => {
    // Set ARIA live region for chat box
    chatBox.setAttribute("role", "list");
    chatBox.setAttribute("aria-live", "polite");

    loadMemory();
    inputField.focus();
});

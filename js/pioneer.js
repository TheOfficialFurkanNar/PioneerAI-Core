// js/pioneer.js (Improved)

// Element referansları
const sendBtn = document.getElementById("sendBtn");
const messageInput = document.getElementById("userInput");
const styleSelect = document.getElementById("summaryStyle");
const chatWindow = document.getElementById("chatWindow");
const streamToggle = document.getElementById("streamToggle");

const API_ENDPOINT_SUMMARY = "/ask/summary";
const API_ENDPOINT_STREAM = "/ask/summary/stream";
const USER_ID_KEY = "userId";
const DEFAULT_USER_ID = "guest";

// Function to get the user ID
function getUserId() {
    return sessionStorage.getItem(USER_ID_KEY) || DEFAULT_USER_ID;
}

//Template for the message
function createMessageElement(who, text) {
    const el = document.createElement("div");
    el.className = who === "user" ? "user-msg" : "bot-msg";
    el.textContent = text;
    return el;
}

// Append Message to chatWindow
function appendMessage(who, text) {
    const el = createMessageElement(who, text);
    chatWindow.appendChild(el);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}


// Common function to send the request
async function sendMessage(endpoint, userMessage, isStream = false) {
    appendMessage("user", userMessage);
    let botEl;

    if (isStream) {
        botEl = document.createElement("div");
        botEl.className = "bot-msg";
        chatWindow.appendChild(botEl);
    } else {
        appendMessage("bot", "…yazıyor");
    }
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: getUserId(),
                prompt: userMessage,
                style: styleSelect.value
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        if (isStream) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let done = false;

            while (!done) {
                const { value, done: readDone } = await reader.read();
                done = readDone;
                const chunk = decoder.decode(value, { stream: true });
                botEl.textContent += chunk;
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }
        } else {
            const data = await response.json();
            chatWindow.lastElementChild.remove(); // Remove "typing..."
            appendMessage("bot", data.response);
        }

    } catch (error) {
        console.error("Error:", error);
        if (isStream && botEl) {
            botEl.textContent = "⚠️ Error: Could not retrieve response.";
        } else if (!isStream) {
            chatWindow.lastElementChild.remove(); // Remove "typing..."
            appendMessage("bot", "⚠️ Error: Could not retrieve response.");
        }
    }
}

// Tek seferlik özet
async function sendSummary() {
    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    await sendMessage(API_ENDPOINT_SUMMARY, userMessage, false);
}

// Akışlı özet
async function sendStreamSummary() {
    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    await sendMessage(API_ENDPOINT_STREAM, userMessage, true);
}


// Buton Click Event
sendBtn.addEventListener("click", () => {
    const userMessage = messageInput.value.trim();
        if (!userMessage) return;

    if (streamToggle.checked) {
        sendStreamSummary();
    } else {
        sendSummary();
    }
     messageInput.value = ""; //Clear input after sending.
});

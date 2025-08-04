// app.js (Improved Version 2)

// Constants
const MAX_HISTORY = 50;
const API_ENDPOINT = "/api/v1/ask"; // Configuration variable
const AUTH_TOKEN_KEY = 'authToken'; //Key for auth token in local storage

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

    addMessage("user", userMsg);
    inputField.value = "";
    inputField.disabled = true;
    sendBtn.disabled = true;

    const loadingDiv = showLoading();
    const t0 = performance.now();

    try {
        const token = localStorage.getItem(AUTH_TOKEN_KEY); // Retrieve token
        if (!token) {
            throw new Error("Authentication token not found. Please log in.");
        }

        const response = await fetch(API_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}` // Add the token
            },
            body: JSON.stringify({ user_message: userMsg })
        });

        if (!response.ok) {
            const errorData = await response.json(); // Try to get error details
            let errorMessage = errorData.detail || `Server returned status code: ${response.status}`;

            //Custom error messages based on status codes (example)
            if (response.status === 401) {
                errorMessage = "Yetkilendirme hatası. Lütfen tekrar giriş yapın."; //Authorization error. Please log in again.
            } else if (response.status === 400) {
                errorMessage = "Geçersiz istek. Lütfen mesajınızı kontrol edin."; //Invalid request. Please check your message.
            }

            throw new Error(errorMessage);
        }

        const data = await response.json();

        removeLoading(loadingDiv);

        const reply = document.createElement("div");
        //Consider sanitizing data.response here if you are not doing it on the backend
        reply.textContent = (data && typeof data.response === "string")
            ? data.response
            : "⚠️ Yanıt alınamadı.";

        addMessage("bot", reply.textContent);
        saveToMemory(userMsg, reply.textContent);

    } catch (error) {
        console.error("API request failed:", error);
        removeLoading(loadingDiv);

        //User-friendly error messages
        let displayError = "⚠️ Bir hata oluştu. Lütfen tekrar deneyin."; //An error occurred. Please try again.
        if (error.message.includes("Authentication token not found")) {
            displayError = "Lütfen giriş yapın."; //Please log in.
        } else if (error.message.includes("Yetkilendirme hatası")) {
            displayError = "Oturumunuz sona erdi. Lütfen tekrar giriş yapın."; //Your session has expired. Please log in again.
        } else {
            displayError = `⚠️ Sunucuya ulaşılamadı: ${error.message}`; //Server unreachable:
        }
        addMessage("bot", displayError);

        //If authentication fails, you might want to redirect to the login page
        if (error.message.includes("Authentication token not found") || error.message.includes("Yetkilendirme hatası")) {
            //Redirect to login page (adjust the path as needed)
            window.location.href = "login.html";
        }

    } finally {
        const t1 = performance.now();
        console.log(`Yanıt süresi: ${(t1 - t0).toFixed(2)} ms`);

        inputField.disabled = false;
        sendBtn.disabled = false;
        inputField.focus();
    }
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

// js/pioneer.js (Improved with Authentication)

// Element referansları
const sendBtn = document.getElementById("sendBtn");
const messageInput = document.getElementById("userInput");
const styleSelect = document.getElementById("summaryStyle");
const chatWindow = document.getElementById("chatWindow");
const streamToggle = document.getElementById("streamToggle");

const API_ENDPOINT_SUMMARY = "http://localhost:5000/ask/summary";
const API_ENDPOINT_STREAM = "http://localhost:5000/ask/summary/stream";
const AUTH_TOKEN_KEY = "auth_token";

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!token) {
        alert('Lütfen önce giriş yapın.');
        window.location.href = 'login.html';
        return;
    }
    
    // Add logout button to chat interface
    addLogoutButton();
});

// Add logout functionality to chat interface
function addLogoutButton() {
    const container = document.querySelector('.container');
    if (container && !document.getElementById('logoutBtn')) {
        const logoutBtn = document.createElement('button');
        logoutBtn.id = 'logoutBtn';
        logoutBtn.textContent = 'Çıkış Yap';
        logoutBtn.style.cssText = 'position: absolute; top: 20px; right: 20px; padding: 8px 16px; background-color: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;';
        logoutBtn.onclick = logout;
        container.appendChild(logoutBtn);
    }
}

// Logout function
function logout() {
    if (confirm('Çıkış yapmak istediğinize emin misiniz?')) {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem('user_info');
        window.location.href = 'login.html';
    }
}

// Get authentication token
function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

// Function to get the user ID from stored user info
function getUserId() {
    const userInfo = localStorage.getItem('user_info');
    if (userInfo) {
        const user = JSON.parse(userInfo);
        return user.id || user.username || 'guest';
    }
    return 'guest';
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
        const token = getAuthToken();
        if (!token) {
            throw new Error('Authentication required');
        }

        const response = await fetch(endpoint, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                user_id: getUserId(),
                prompt: userMessage,
                style: styleSelect.value
            })
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem(AUTH_TOKEN_KEY);
                localStorage.removeItem('user_info');
                alert('Oturumunuz sona erdi. Lütfen tekrar giriş yapın.');
                window.location.href = 'login.html';
                return;
            }
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

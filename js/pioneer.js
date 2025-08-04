// js/pioneer.js - JWT Authenticated Chat Interface

// Element referansları
const sendBtn = document.getElementById("sendBtn");
const messageInput = document.getElementById("userInput");
const styleSelect = document.getElementById("summaryStyle");
const chatWindow = document.getElementById("chatWindow");
const streamToggle = document.getElementById("streamToggle");

const API_ENDPOINT_SUMMARY = "/ask/summary";
const API_ENDPOINT_STREAM = "/ask/summary/stream";
const AUTH_TOKEN_KEY = "auth_token";
const LOGIN_URL = "/html/login.html";
const SESSION_TIMEOUT = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

// Check if user is authenticated and session is valid
function isAuthenticated() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const loginTime = localStorage.getItem('login_time');
    
    if (!token || !loginTime) {
        return false;
    }
    
    // Check if session has expired
    const currentTime = new Date().getTime();
    const sessionAge = currentTime - parseInt(loginTime);
    
    if (sessionAge > SESSION_TIMEOUT) {
        // Session expired, clear storage
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem('login_time');
        return false;
    }
    
    return true;
}

// Redirect to login if not authenticated
function redirectToLogin() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    window.location.replace(LOGIN_URL);
}

// Navigate to dashboard
function goToDashboard() {
    window.location.href = "/html/dashboard.html";
}

// Logout function
async function logout() {
    if (!confirm("Çıkış yapmak istediğinize emin misiniz?")) {
        return;
    }
    
    const authToken = localStorage.getItem(AUTH_TOKEN_KEY);
    
    if (authToken) {
        try {
            await fetch("/auth/logout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${authToken}`
                }
            });
        } catch (error) {
            console.error("Logout error:", error);
        }
    }
    
    localStorage.removeItem(AUTH_TOKEN_KEY);
    window.location.replace(LOGIN_URL);
}

// Get authentication headers
function getAuthHeaders() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
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
    // Check authentication before sending
    if (!isAuthenticated()) {
        appendMessage("bot", "⚠️ Oturumunuz sona erdi. Lütfen tekrar giriş yapın.");
        setTimeout(() => redirectToLogin(), 2000);
        return;
    }

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
            headers: getAuthHeaders(),
            body: JSON.stringify({
                prompt: userMessage,
                style: styleSelect.value
            })
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                if (isStream && botEl) {
                    botEl.textContent = "⚠️ Oturumunuz sona erdi. Giriş sayfasına yönlendiriliyorsunuz...";
                } else if (!isStream) {
                    chatWindow.lastElementChild.remove();
                    appendMessage("bot", "⚠️ Oturumunuz sona erdi. Giriş sayfasına yönlendiriliyorsunuz...");
                }
                setTimeout(() => redirectToLogin(), 2000);
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
            botEl.textContent = "⚠️ Hata: Yanıt alınamadı. Lütfen tekrar deneyin.";
        } else if (!isStream) {
            chatWindow.lastElementChild.remove(); // Remove "typing..."
            appendMessage("bot", "⚠️ Hata: Yanıt alınamadı. Lütfen tekrar deneyin.");
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


// Handle form submission
function handleSubmit(event) {
    event.preventDefault();
    
    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    if (streamToggle.checked) {
        sendStreamSummary();
    } else {
        sendSummary();
    }
    messageInput.value = ""; // Clear input after sending
}

// DOM Content Loaded Event
document.addEventListener("DOMContentLoaded", () => {
    // Check authentication on page load
    if (!isAuthenticated()) {
        appendMessage("bot", "⚠️ Lütfen önce giriş yapın.");
        setTimeout(() => redirectToLogin(), 2000);
        return;
    }
    
    // Show navigation bar for authenticated users
    const navBar = document.getElementById("navBar");
    if (navBar) {
        navBar.style.display = "block";
    }
    
    // Add welcome message
    appendMessage("bot", "Merhaba! Size nasıl yardımcı olabilirim?");
    
    // Attach form submit event
    const chatForm = document.getElementById("chatForm");
    if (chatForm) {
        chatForm.addEventListener("submit", handleSubmit);
    }
    
    // Attach button click event as fallback
    if (sendBtn) {
        sendBtn.addEventListener("click", handleSubmit);
    }
    
    // Handle Enter key in textarea
    if (messageInput) {
        messageInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
            }
        });
    }
});

// js/pioneer.js

// Element referansları
const sendBtn = document.getElementById("sendBtn");
const messageInput = document.getElementById("userInput");
const styleSelect = document.getElementById("summaryStyle");
const chatWindow = document.getElementById("chatWindow");
const streamToggle = document.getElementById("streamToggle");

// Temizleme yardımcı fonksiyonu
function appendMessage(who, text) {
    const el = document.createElement("div");
    el.className = who === "user" ? "user-msg" : "bot-msg";
    el.textContent = text;
    chatWindow.appendChild(el);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Tek seferlik özet
async function sendSummary() {
    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    appendMessage("user", userMessage);
    appendMessage("bot", "…yazıyor");

    const res = await fetch("/ask/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: sessionStorage.getItem("userId") || "guest",
            prompt: userMessage,
            style: styleSelect.value
        })
    });
    const data = await res.json();

    // “…yazıyor” u kaldır ve sonucu yaz
    chatWindow.lastElementChild.remove();
    appendMessage("bot", data.response);
}

// Akışlı özet
async function sendStreamSummary() {
    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    appendMessage("user", userMessage);
    const botEl = document.createElement("div");
    botEl.className = "bot-msg";
    botEl.textContent = "";
    chatWindow.appendChild(botEl);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    const response = await fetch("/ask/summary/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: sessionStorage.getItem("userId") || "guest",
            prompt: userMessage,
            style: styleSelect.value
        })
    });

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
}

// Buton Click Event
sendBtn.addEventListener("click", () => {
    if (streamToggle.checked) {
        sendStreamSummary();
    } else {
        sendSummary();
    }
});

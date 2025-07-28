// app.js

// Sabitler
const MAX_HISTORY = 50;

const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("input-field");
const sendBtn = document.getElementById("send-btn");

// Mesajları DOM'a ekler
function addMessage(sender, text) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// LocalStorage'dan geçmişi yükler
function loadMemory() {
    try {
        const history = JSON.parse(localStorage.getItem("chat_history")) || [];
        if (!Array.isArray(history)) throw new Error("Hafıza formatı yanlış!");
        const limitedHistory = history.slice(-MAX_HISTORY);

        limitedHistory.forEach(entry => {
            if (entry.user && entry.bot) {
                addMessage("user", entry.user);
                addMessage("bot", entry.bot);
            }
        });
    } catch (e) {
        console.warn("Yerel hafıza okunamadı veya bozuk. Sıfırlanıyor.", e);
        localStorage.removeItem("chat_history");
    }
}

// LocalStorage'a mesaj kaydeder, maksimum kayıt sınırını kontrol eder
function saveToMemory(userMsg, botReply) {
    try {
        let history = JSON.parse(localStorage.getItem("chat_history")) || [];
        if (!Array.isArray(history)) history = [];

        if (history.length >= MAX_HISTORY) {
            history.shift();
        }

        history.push({ user: userMsg, bot: botReply });
        localStorage.setItem("chat_history", JSON.stringify(history));
    } catch (e) {
        console.warn("Yerel hafıza kaydedilemedi:", e);
    }
}

// API'ye mesaj gönderir ve yanıtı alır
async function sendMessage() {
    const userMsg = inputField.value.trim();
    if (!userMsg) return;

    // Kullanıcı mesajını ekle ve input'u temizle
    addMessage("user", userMsg);
    inputField.value = "";
    inputField.disabled = true;
    sendBtn.disabled = true;

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

        const botReply = (data && typeof data.response === "string")
            ? data.response
            : "⚠️ Yanıt alınamadı.";

        addMessage("bot", botReply);
        saveToMemory(userMsg, botReply);

    } catch (error) {
        console.error("API isteği başarısız:", error);
        addMessage("bot", "⚠️ Sunucuya ulaşılamadı.");
    }

    const t1 = performance.now();
    console.log(`Yanıt süresi: ${(t1 - t0).toFixed(2)} ms`);

    inputField.disabled = false;
    sendBtn.disabled = false;
    inputField.focus();
}

// Klavye dinleyicisi (Enter gönder, Shift+Enter yeni satır)
inputField.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Buton dinleyicisi
sendBtn.addEventListener("click", sendMessage);

// Sayfa yüklendiğinde hafızayı yükle ve inputa odaklan
window.addEventListener("DOMContentLoaded", () => {
    loadMemory();
    inputField.focus();
});

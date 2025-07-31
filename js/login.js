// login.js (Refactored & Enhanced)

// Utility for safe DOM updates
function setSafeText(id, value, fallback = "") {
    const el = document.getElementById(id);
    if (el) el.innerText = value || fallback;
}

// Main login function
function loginUser() {
    const username = document.getElementById("uname")?.value.trim();
    const password = document.getElementById("pwd")?.value.trim();
    const statusEl = document.getElementById("status");

    // Accessibility: Announce status updates
    if (statusEl) statusEl.setAttribute("aria-live", "polite");

    if (!username || !password) {
        setSafeText("status", "Lütfen tüm alanları doldurun!");
        return;
    }

    setSafeText("status", "Giriş yapılıyor...");

    fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
        .then(res => {
            if (!res.ok) throw new Error("Yanıt alınamadı");
            return res.json();
        })
        .then(data => {
            if (data.api_key) {
                setSafeText("status", `✅ Giriş başarılı! API Anahtarınız: ${data.api_key}`);
                localStorage.setItem("api_key", data.api_key);
                // Optionally redirect to dashboard
                setTimeout(() => {
                    window.location.href = "../html/dashboard.html";
                }, 1200);
            } else if (data.error) {
                setSafeText("status", `❌ ${data.error}`);
            } else {
                setSafeText("status", "❔ Giriş başarısız!");
            }
        })
        .catch(err => {
            console.error("Hata:", err);
            setSafeText("status", "⚠️ Sunucuya ulaşılamadı.");
        });
}

// Support pressing Enter in password field to trigger login
const pwdInput = document.getElementById("pwd");
if (pwdInput) {
    pwdInput.addEventListener("keydown", e => {
        if (e.key === "Enter") {
            loginUser();
        }
    });
}

// Attach login function to button
const loginBtn = document.getElementById("loginBtn");
if (loginBtn) {
    loginBtn.addEventListener("click", loginUser);
}
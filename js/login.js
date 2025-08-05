// login.js (Refactored & Enhanced - COOKIE BASED)

const API_ENDPOINT_LOGIN = "http://localhost:5000/login"; // Configuration
const DASHBOARD_URL = "../html/dashboard.html";

// Utility for safe DOM updates
function setSafeText(id, value, fallback = "") {
    const el = document.getElementById(id);
    if (el) el.innerText = value || fallback;
}

// Main login function
async function loginUser() {
    const username = document.getElementById("uname")?.value.trim();
    const password = document.getElementById("pwd")?.value.trim();
    const statusEl = document.getElementById("status");
    const loginBtn = document.getElementById("loginBtn"); //Disable button while loading

    // Accessibility: Announce status updates
    if (statusEl) statusEl.setAttribute("aria-live", "polite");

    if (!username || !password) {
        setSafeText("status", "Lütfen tüm alanları doldurun!");
        return;
    }

    setSafeText("status", "Giriş yapılıyor...");
    if (loginBtn) loginBtn.disabled = true;

    try {
        const response = await fetch(API_ENDPOINT_LOGIN, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            let message = `Giriş başarısız. Hata kodu: ${response.status}`;
            if(response.status === 401 || response.status === 403) {
                message = "Kullanıcı adı veya şifre hatalı.";
            }
            throw new Error(message);
        }

        const data = await response.json();

        if (data.message === "Login successful") { //Check success message
            //Token is now handled by cookie.  No need to access it from javascript
            setSafeText("status", "✅ Giriş başarılı! Yönlendiriliyorsunuz..."); //Inform the user
            // Optionally redirect to dashboard
            setTimeout(() => {
                window.location.href = DASHBOARD_URL;
            }, 1200);
        } else if (data.error) {
            setSafeText("status", `❌ ${data.error}`);
        } else {
            setSafeText("status", "❔ Giriş başarısız!");
        }
    } catch (err) {
        console.error("Hata:", err);
        setSafeText("status", err.message || "⚠️ Sunucuya ulaşılamadı."); //Show the error message
    } finally {
       if (loginBtn) loginBtn.disabled = false;
    }
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
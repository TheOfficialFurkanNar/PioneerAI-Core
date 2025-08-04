// login.js (JWT Token Based Authentication)

const API_ENDPOINT_LOGIN = "http://localhost:5000/login";
const DASHBOARD_URL = "dashboard.html";

// Utility for safe DOM updates
function setSafeText(id, value, fallback = "") {
    const el = document.getElementById(id);
    if (el) el.innerText = value || fallback;
}

// Token management
function saveToken(token) {
    localStorage.setItem('auth_token', token);
}

function getToken() {
    return localStorage.getItem('auth_token');
}

function removeToken() {
    localStorage.removeItem('auth_token');
}

// Main login function
async function loginUser() {
    const username = document.getElementById("uname")?.value.trim();
    const password = document.getElementById("pwd")?.value.trim();
    const statusEl = document.getElementById("serverError");
    const loginBtn = document.getElementById("loginBtn");

    // Clear previous errors
    setSafeText("serverError", "");

    // Accessibility: Announce status updates
    if (statusEl) statusEl.setAttribute("aria-live", "polite");

    if (!username || !password) {
        setSafeText("serverError", "Lütfen tüm alanları doldurun!");
        return;
    }

    setSafeText("serverError", "Giriş yapılıyor...");
    if (loginBtn) loginBtn.disabled = true;

    try {
        const response = await fetch(API_ENDPOINT_LOGIN, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.token) {
            // Save token and user info
            saveToken(data.token);
            localStorage.setItem('user_info', JSON.stringify(data.user));
            
            setSafeText("serverError", "✅ Giriş başarılı! Yönlendiriliyorsunuz...");
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = DASHBOARD_URL;
            }, 1200);
        } else {
            setSafeText("serverError", `❌ ${data.error || 'Giriş başarısız!'}`);
        }
    } catch (err) {
        console.error("Hata:", err);
        setSafeText("serverError", "⚠️ Sunucuya ulaşılamadı.");
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
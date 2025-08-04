// registry.js (JWT Token Based Registration)

const API_ENDPOINT_REGISTER = "http://localhost:5000/register";
const LOGIN_URL = "login.html";

// Utility for safe DOM updates
function setSafeText(id, value, fallback = "") {
    const el = document.getElementById(id);
    if (el) el.innerText = value || fallback;
}

// Token management
function saveToken(token) {
    localStorage.setItem('auth_token', token);
}

// Input validation
function validateUsername(username) {
    const pattern = /^[a-zA-Z0-9_]{3,20}$/;
    return pattern.test(username);
}

function validateEmail(email) {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
}

function validatePassword(password) {
    return password.length >= 8;
}

// Clear all error messages
function clearErrors() {
    setSafeText("regUnameError", "");
    setSafeText("regEmailError", "");
    setSafeText("regPwdError", "");
    setSafeText("regServerError", "");
}

// Main registration function
async function registerUser() {
    const username = document.getElementById("regUname")?.value.trim();
    const email = document.getElementById("regEmail")?.value.trim().toLowerCase();
    const password = document.getElementById("regPwd")?.value;
    const registerBtn = document.getElementById("registerBtn");

    // Clear previous errors
    clearErrors();

    let hasErrors = false;

    // Client-side validation
    if (!username) {
        setSafeText("regUnameError", "Kullanıcı adı gereklidir");
        hasErrors = true;
    } else if (!validateUsername(username)) {
        setSafeText("regUnameError", "Kullanıcı adı 3-20 karakter olmalı ve sadece harf, rakam, alt çizgi içermelidir");
        hasErrors = true;
    }

    if (!email) {
        setSafeText("regEmailError", "E-posta gereklidir");
        hasErrors = true;
    } else if (!validateEmail(email)) {
        setSafeText("regEmailError", "Geçersiz e-posta formatı");
        hasErrors = true;
    }

    if (!password) {
        setSafeText("regPwdError", "Şifre gereklidir");
        hasErrors = true;
    } else if (!validatePassword(password)) {
        setSafeText("regPwdError", "Şifre en az 8 karakter olmalıdır");
        hasErrors = true;
    }

    if (hasErrors) {
        return;
    }

    setSafeText("regServerError", "Kayıt oluşturuluyor...");
    if (registerBtn) registerBtn.disabled = true;

    try {
        const response = await fetch(API_ENDPOINT_REGISTER, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok && data.token) {
            // Save token and user info
            saveToken(data.token);
            localStorage.setItem('user_info', JSON.stringify(data.user));
            
            setSafeText("regServerError", "✅ Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...");
            
            // Redirect to login page
            setTimeout(() => {
                window.location.href = LOGIN_URL;
            }, 2000);
        } else {
            setSafeText("regServerError", `❌ ${data.error || 'Kayıt başarısız!'}`);
        }
    } catch (err) {
        console.error("Hata:", err);
        setSafeText("regServerError", "⚠️ Sunucuya ulaşılamadı.");
    } finally {
       if (registerBtn) registerBtn.disabled = false;
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Register button click
    const registerBtn = document.getElementById("registerBtn");
    if (registerBtn) {
        registerBtn.addEventListener("click", function(e) {
            e.preventDefault();
            registerUser();
        });
    }

    // Form submission
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", function(e) {
            e.preventDefault();
            registerUser();
        });
    }

    // Enter key support
    const passwordInput = document.getElementById("regPwd");
    if (passwordInput) {
        passwordInput.addEventListener("keydown", function(e) {
            if (e.key === "Enter") {
                e.preventDefault();
                registerUser();
            }
        });
    }
});
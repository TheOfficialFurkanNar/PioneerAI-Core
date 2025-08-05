// js/registry.js - User Registration Functionality

const API_ENDPOINT_REGISTER = "/auth/register";
const LOGIN_URL = "/html/login.html";

// Utility function for safe DOM updates
function setSafeText(id, value, fallback = "") {
    const el = document.getElementById(id);
    if (el) el.innerText = value || fallback;
}

// Client-side validation functions
function validateUsername(username) {
    if (!username || username.length < 3 || username.length > 20) {
        return { valid: false, message: "Kullanıcı adı 3-20 karakter arasında olmalıdır." };
    }
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        return { valid: false, message: "Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir." };
    }
    return { valid: true };
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        return { valid: false, message: "Geçerli bir e-posta adresi giriniz." };
    }
    return { valid: true };
}

function validatePassword(password) {
    if (!password || password.length < 8) {
        return { valid: false, message: "Şifre en az 8 karakter olmalıdır." };
    }
    return { valid: true };
}

// Clear error messages
function clearErrors() {
    setSafeText("regUnameError", "");
    setSafeText("regEmailError", "");
    setSafeText("regPwdError", "");
    setSafeText("regServerError", "");
}

// Show success message
function showSuccess(message) {
    setSafeText("regServerError", `✅ ${message}`);
    const errorEl = document.getElementById("regServerError");
    if (errorEl) {
        errorEl.style.color = "green";
    }
}

// Show error message
function showError(message) {
    setSafeText("regServerError", `❌ ${message}`);
    const errorEl = document.getElementById("regServerError");
    if (errorEl) {
        errorEl.style.color = "red";
    }
}

// Main registration function
async function registerUser(event) {
    event.preventDefault();

    const username = document.getElementById("regUname")?.value.trim();
    const email = document.getElementById("regEmail")?.value.trim();
    const password = document.getElementById("regPwd")?.value.trim();
    const registerBtn = document.getElementById("registerBtn");

    // Clear previous errors
    clearErrors();

    // Client-side validation
    const usernameValidation = validateUsername(username);
    if (!usernameValidation.valid) {
        setSafeText("regUnameError", usernameValidation.message);
        return;
    }

    const emailValidation = validateEmail(email);
    if (!emailValidation.valid) {
        setSafeText("regEmailError", emailValidation.message);
        return;
    }

    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
        setSafeText("regPwdError", passwordValidation.message);
        return;
    }

    // Show loading state
    if (registerBtn) {
        registerBtn.disabled = true;
        registerBtn.textContent = "Kayıt yapılıyor...";
    }

    try {
        const response = await fetch(API_ENDPOINT_REGISTER, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showSuccess("Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...");

            // Redirect to login page after 2 seconds
            setTimeout(() => {
                window.location.href = LOGIN_URL;
            }, 2000);
        } else {
            // Handle server-side validation errors
            const errorMessage = data.message || "Kayıt işlemi başarısız oldu.";
            showError(errorMessage);
        }

    } catch (error) {
        console.error("Registration error:", error);
        showError("Sunucuya ulaşılamadı. Lütfen tekrar deneyin.");
    } finally {
        // Reset button state
        if (registerBtn) {
            registerBtn.disabled = false;
            registerBtn.textContent = "Kayıt Ol";
        }
    }
}

// DOM Content Loaded Event
document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", registerUser);
    }

    // Real-time validation feedback
    const usernameInput = document.getElementById("regUname");
    const emailInput = document.getElementById("regEmail");
    const passwordInput = document.getElementById("regPwd");

    if (usernameInput) {
        usernameInput.addEventListener("blur", () => {
            const validation = validateUsername(usernameInput.value.trim());
            setSafeText("regUnameError", validation.valid ? "" : validation.message);
        });
    }

    if (emailInput) {
        emailInput.addEventListener("blur", () => {
            const validation = validateEmail(emailInput.value.trim());
            setSafeText("regEmailError", validation.valid ? "" : validation.message);
        });
    }

    if (passwordInput) {
        passwordInput.addEventListener("blur", () => {
            const validation = validatePassword(passwordInput.value.trim());
            setSafeText("regPwdError", validation.valid ? "" : validation.message);
        });
    }
});
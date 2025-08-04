// js/login.js - JWT Token Based Authentication

const API_ENDPOINT_LOGIN = "/auth/login";
const DASHBOARD_URL = "/html/dashboard.html";
const AUTH_TOKEN_KEY = "auth_token";

// Utility for safe DOM updates
function setSafeText(id, value, fallback = "") {
    const el = document.getElementById(id);
    if (el) el.innerText = value || fallback;
}

// Show error message
function showError(message) {
    setSafeText("serverError", `❌ ${message}`);
}

// Show success message
function showSuccess(message) {
    setSafeText("serverError", `✅ ${message}`);
}

// Main login function
async function loginUser(event) {
    event.preventDefault();
    
    const username = document.getElementById("uname")?.value.trim();
    const password = document.getElementById("pwd")?.value.trim();
    const loginBtn = document.getElementById("loginBtn");

    if (!username || !password) {
        showError("Lütfen tüm alanları doldurun!");
        return;
    }

    // Show loading state
    if (loginBtn) {
        loginBtn.disabled = true;
        loginBtn.textContent = "Giriş yapılıyor...";
    }
    
    setSafeText("serverError", "Giriş yapılıyor...");

    try {
        const response = await fetch(API_ENDPOINT_LOGIN, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Store JWT token and login time in localStorage
            localStorage.setItem(AUTH_TOKEN_KEY, data.token);
            localStorage.setItem('login_time', new Date().getTime().toString());
            
            showSuccess("Giriş başarılı! Yönlendiriliyorsunuz...");
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = DASHBOARD_URL;
            }, 1200);
        } else {
            const errorMessage = data.message || "Giriş başarısız!";
            showError(errorMessage);
        }
    } catch (err) {
        console.error("Login error:", err);
        showError("Sunucuya ulaşılamadı. Lütfen tekrar deneyin.");
    } finally {
        // Reset button state
        if (loginBtn) {
            loginBtn.disabled = false;
            loginBtn.textContent = "Giriş Yap";
        }
    }
}

// Password toggle functionality
function togglePassword() {
    const pwdInput = document.getElementById("pwd");
    const toggleBtn = document.getElementById("togglePassword");
    
    if (pwdInput && toggleBtn) {
        if (pwdInput.type === "password") {
            pwdInput.type = "text";
            toggleBtn.textContent = "Gizle";
            toggleBtn.setAttribute("aria-expanded", "true");
        } else {
            pwdInput.type = "password";
            toggleBtn.textContent = "Göster";
            toggleBtn.setAttribute("aria-expanded", "false");
        }
    }
}

// DOM Content Loaded Event
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const toggleBtn = document.getElementById("togglePassword");
    
    // Attach form submit event
    if (loginForm) {
        loginForm.addEventListener("submit", loginUser);
    }
    
    // Attach password toggle event
    if (toggleBtn) {
        toggleBtn.addEventListener("click", togglePassword);
    }
});
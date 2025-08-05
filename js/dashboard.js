// js/dashboard.js - JWT Token Based Dashboard

const API_ENDPOINT_USERINFO = "/auth/userinfo";
const API_ENDPOINT_LOGOUT = "/auth/logout";
const AUTH_TOKEN_KEY = "auth_token";
const LOGIN_URL = "/html/login.html";
const CHAT_URL = "/html/index.html";
const SESSION_TIMEOUT = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

// Utility: Set text or fallback
function setSafeText(id, value, fallback = "[Bilinmiyor]") {
    const el = document.getElementById(id);
    if (el) el.innerText = value || fallback;
}

// Show alert function
function showAlert(message) {
    alert(message);
}

// Check if user is authenticated
function isAuthenticated() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    return token !== null && token !== "";
}

// Redirect to login if not authenticated
function redirectToLogin() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    window.location.replace(LOGIN_URL);
}

// Load user information
async function loadUserInfo() {
    const authToken = localStorage.getItem(AUTH_TOKEN_KEY);
<<<<<<< HEAD

=======

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    if (!authToken) {
        showAlert("Oturumunuz sona erdi. Lütfen tekrar giriş yapın.");
        redirectToLogin();
        return;
    }

    // Show loading state
    setSafeText("userName", "Yükleniyor...");
    setSafeText("apiKey", "Yükleniyor...");
    setSafeText("emailStatus", "Yükleniyor...");
    setSafeText("lastLogin", "Yükleniyor...");

    try {
        const response = await fetch(API_ENDPOINT_USERINFO, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                showAlert("Oturumunuz sona erdi. Lütfen tekrar giriş yapın.");
                redirectToLogin();
                return;
            }
            throw new Error(`Kullanıcı bilgisi alınamadı. Hata kodu: ${response.status}`);
        }

        const data = await response.json();

        if (data.success && data.user) {
            setSafeText("userName", data.user.username);
            setSafeText("apiKey", "API Anahtarı Ayarlandı");
            setSafeText("emailStatus", "Aktif"); // Since we don't have email verification yet
            setSafeText("lastLogin", data.user.last_login || "İlk giriş");
        } else {
            throw new Error("Kullanıcı bilgisi alınamadı.");
        }

    } catch (err) {
        console.error("Dashboard error:", err);
        showAlert(err.message || "Kullanıcı bilgisi alınamadı. Lütfen tekrar giriş yapın.");
        redirectToLogin();
    }
}

// Logout function with server call
async function logout() {
    if (!confirm("Çıkış yapmak istediğinize emin misiniz?")) {
        return;
    }
<<<<<<< HEAD

    const authToken = localStorage.getItem(AUTH_TOKEN_KEY);

=======

    const authToken = localStorage.getItem(AUTH_TOKEN_KEY);

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    if (authToken) {
        try {
            // Call logout endpoint
            await fetch(API_ENDPOINT_LOGOUT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${authToken}`
                }
            });
        } catch (error) {
            console.error("Logout error:", error);
            // Continue with logout even if server call fails
        }
    }
<<<<<<< HEAD

=======

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    // Remove token and redirect
    localStorage.removeItem(AUTH_TOKEN_KEY);
    window.location.replace(LOGIN_URL);
}

// Navigate to chat interface
function goToChat() {
    window.location.href = "/html/index.html";
}

// DOM Content Loaded Event
document.addEventListener("DOMContentLoaded", () => {
    // Check authentication on page load
    if (!isAuthenticated()) {
        redirectToLogin();
        return;
    }
<<<<<<< HEAD

=======

>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
    // Load user information
    loadUserInfo();
});
// dashboard.js (JWT Token Based Authentication)

const API_ENDPOINT_USERINFO = "http://localhost:5000/userinfo";
const API_ENDPOINT_LOGOUT = "http://localhost:5000/logout";
const AUTH_TOKEN_KEY = 'auth_token';

document.addEventListener("DOMContentLoaded", async () => {
    const authToken = localStorage.getItem(AUTH_TOKEN_KEY);

    // Utility: Set text or fallback
    function setSafeText(id, value, fallback = "[Bilinmiyor]") {
        const el = document.getElementById(id);
        if (el) el.innerText = value || fallback;
    }

    // Show loading state
    setSafeText("userName", "Yükleniyor...");
    setSafeText("userEmail", "Yükleniyor...");
    setSafeText("lastLogin", "Yükleniyor...");

    if (!authToken) {
        showAlert("Oturumunuz sona erdi. Lütfen tekrar giriş yapın.");
        window.location.replace("login.html");
        return;
    }

    try {
        const response = await fetch(API_ENDPOINT_USERINFO, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${authToken}`
            },
            body: JSON.stringify({})
        });

        if (!response.ok) {
            let message = `Kullanıcı bilgisi alınamadı. Hata kodu: ${response.status}`;
            if(response.status === 401) {
                message = "Yetkilendirme hatası. Lütfen tekrar giriş yapın.";
            }
            throw new Error(message);
        }

        const data = await response.json();

        setSafeText("userName", data.user.username);
        setSafeText("userEmail", data.user.email);
        setSafeText("lastLogin", data.user.last_login ? 
            new Date(data.user.last_login).toLocaleString('tr-TR') : 
            "İlk giriş");

    } catch (err) {
        console.error("Hata:", err);
        showAlert(err.message || "Kullanıcı bilgisi alınamadı. Lütfen tekrar giriş yapın.");
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem('user_info');
        window.location.replace("login.html");
    }
});

// Show alert function
function showAlert(message) {
    alert(message);
}

// Logout function
async function logout() {
    if (confirm("Çıkış yapmak istediğinize emin misiniz?")) {
        const authToken = localStorage.getItem(AUTH_TOKEN_KEY);
        
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
            } catch (err) {
                console.error("Logout error:", err);
            }
        }
        
        // Clear local storage
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem('user_info');
        
        // Redirect to login
        window.location.replace("login.html");
    }
}
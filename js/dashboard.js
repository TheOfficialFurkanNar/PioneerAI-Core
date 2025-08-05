// dashboard.js (Refactored & Enhanced)

const API_ENDPOINT_USERINFO = "http://localhost:5000/userinfo"; // Configuration
const AUTH_TOKEN_KEY = 'authToken'; // Consistent naming

document.addEventListener("DOMContentLoaded", async () => { //async
    const authToken = localStorage.getItem(AUTH_TOKEN_KEY); //Use authToken, not api_key

    // Utility: Set text or fallback
    function setSafeText(id, value, fallback = "[Bilinmiyor]") {
        const el = document.getElementById(id);
        if (el) el.innerText = value || fallback;
    }

    // Show loading state
    setSafeText("userName", "Yükleniyor...");
    setSafeText("apiKey", "Yükleniyor...");
    setSafeText("emailStatus", "Yükleniyor...");
    setSafeText("lastLogin", "Yükleniyor...");

    if (!authToken) { //Check for auth token
        showAlert("Oturumunuz sona erdi. Lütfen tekrar giriş yapın."); //More user friendly
        window.location.replace("../html/login.html");  //Use replace
        return;
    }

    try {
        const response = await fetch(API_ENDPOINT_USERINFO, { //await
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${authToken}` //Send auth token
            },
            body: JSON.stringify({}) //No need to send anything in the body
        });

        if (!response.ok) {
            let message = `Kullanıcı bilgisi alınamadı. Hata kodu: ${response.status}`;
            if(response.status === 401) {
                message = "Yetkilendirme hatası. Lütfen tekrar giriş yapın.";
            }
            throw new Error(message);
        }

        const data = await response.json();

        setSafeText("userName", data.username);
        //Don't show the API key
        setSafeText("apiKey", "API Anahtarı Ayarlandı"); //More secure
        setSafeText("emailStatus", data.email_verified ? "Doğrulandı" : "Doğrulanmadı");
        setSafeText("lastLogin", data.last_login);

    } catch (err) {
        console.error("Hata:", err);
        showAlert(err.message || "Kullanıcı bilgisi alınamadı. Lütfen tekrar giriş yapın."); //Show message
        window.location.replace("../html/login.html"); //Use replace

    }
});

// Show alert function (replace with your preferred method)
function showAlert(message) {
    alert(message); //Replace this with a better UI element
}


// Confirm logout for better UX
function logout() {
    if (confirm("Çıkış yapmak istediğinize emin misiniz?")) {
        localStorage.removeItem(AUTH_TOKEN_KEY); //Remove the token
        window.location.replace("../html/login.html"); //Use replace
    }
}
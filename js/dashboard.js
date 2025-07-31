// dashboard.js (Refactored & Enhanced)

document.addEventListener("DOMContentLoaded", () => {
    const apiKey = localStorage.getItem("api_key");

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

    if (!apiKey) {
        alert("API anahtarı bulunamadı. Lütfen yeniden giriş yapın.");
        window.location.href = "../html/login.html";
        return;
    }

    fetch("http://localhost:5000/userinfo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey })
    })
        .then(res => {
            if (!res.ok) throw new Error("Yanıt alınamadı");
            return res.json();
        })
        .then(data => {
            setSafeText("userName", data.username);
            setSafeText("apiKey", apiKey);
            setSafeText("emailStatus", data.email_verified ? "Doğrulandı" : "Doğrulanmadı");
            setSafeText("lastLogin", data.last_login);
        })
        .catch(err => {
            console.error("Hata:", err);
            alert("Kullanıcı bilgisi alınamadı. Lütfen tekrar giriş yapın.");
            window.location.href = "../html/login.html";
        });
});

// Optional: Confirm logout for better UX
function logout() {
    if (confirm("Çıkış yapmak istediğinize emin misiniz?")) {
        localStorage.removeItem("api_key");
        window.location.href = "../html/login.html";
    }
}
document.addEventListener("DOMContentLoaded", () => {
    const apiKey = localStorage.getItem("api_key");

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
        .then(res => res.json())
        .then(data => {
            document.getElementById("userName").innerText = data.username;
            document.getElementById("apiKey").innerText = apiKey;
            document.getElementById("emailStatus").innerText = data.email_verified ? "Doğrulandı" : "Doğrulanmadı";
            document.getElementById("lastLogin").innerText = data.last_login || "Bilinmiyor";
        })
        .catch(err => {
            console.error("Hata:", err);
            alert("Kullanıcı bilgisi alınamadı.");
        });
});

function logout() {
    localStorage.removeItem("api_key");
    window.location.href = "../html/login.html";
}
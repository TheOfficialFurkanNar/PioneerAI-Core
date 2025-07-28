function loginUser() {
    const username = document.getElementById("uname").value.trim();
    const password = document.getElementById("pwd").value.trim();

    if (!username || !password) {
        document.getElementById("status").innerText = "Lütfen tüm alanları doldurun!";
        return;
    }

    fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
        .then(res => res.json())
        .then(data => {
            if (data.api_key) {
                document.getElementById("status").innerText =
                    "? Giriş başarılı! API Anahtarınız: " + data.api_key;

                // Anahtarı saklama (İsteğe bağlı)
                localStorage.setItem("api_key", data.api_key);
            } else if (data.error) {
                document.getElementById("status").innerText = "?? " + data.error;
            } else {
                document.getElementById("status").innerText = "? Giriş başarısız!";
            }
        })
        .catch(err => {
            console.error("Hata:", err);
            document.getElementById("status").innerText = "? Sunucuya ulaşılamadı.";
        });
}
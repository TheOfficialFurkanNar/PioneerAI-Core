let attemptCount = 0;
let captchaRequired = false;

function verifyCode() {
    const code = document.getElementById("veriCode").value.trim();
    const captchaInput = document.getElementById("captchaInput")?.value?.trim();

    // ?? Kod kontrolü öncesi: geçersizlik önlemi
    if (!code || code.length !== 6 || isNaN(code)) {
        document.getElementById("verifyStatus").innerText = "?? Geçerli 6 haneli bir kod giriniz.";
        return;
    }

    // ?? CAPTCHA devredeyse önce onu kontrol et
    if (captchaRequired && captchaInput !== "jp67y") {
        document.getElementById("verifyStatus").innerText = "? Karakter dizisi yanlış. Bot olabileceğiniz algılandı.";
        return;
    }

    // ?? Backend'e doğrulama isteği gönder
    fetch("http://localhost:5000/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                document.getElementById("verifyStatus").innerText = "? Doğrulama başarılı! PioneerAI paneline yönlendiriliyorsunuz...";
                attemptCount = 0;
                captchaRequired = false;

                setTimeout(() => {
                    window.location.href = "../html/dashboard.html";
                }, 2000);
            } else {
                attemptCount++;

                if (attemptCount >= 3 && !captchaRequired) {
                    captchaRequired = true;
                    const captchaHtml = `
          <p>Lütfen bot olmadığınızı doğrulayın: <strong>jp67y</strong></p>
          <input id="captchaInput" type="text" placeholder="jp67y">
        `;
                    document.getElementById("verifyBox").insertAdjacentHTML("beforeend", captchaHtml);
                }

                document.getElementById("verifyStatus").innerText =
                    "? Kod hatalı! " + (captchaRequired ? "Doğrulamak için karakter dizisini giriniz." : "Tekrar deneyin.");
            }
        })
        .catch(error => {
            console.error("Sunucu hatası:", error);
            document.getElementById("verifyStatus").innerText = "? Sunucuya erişilemiyor.";
        });
}
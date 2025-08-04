// verify.js (Refactored & Enhanced - RECAPTCHA INTEGRATED)

const API_ENDPOINT_VERIFY = "http://localhost:5000/verify"; // Configuration
const DASHBOARD_URL = "../html/dashboard.html";

async function verifyCode() {
    const code = document.getElementById("veriCode").value.trim();
    const verifyStatusEl = document.getElementById("verifyStatus");

    // ?? Kod kontrolü öncesi: geçersizlik önlemi
    if (!code || code.length !== 6 || isNaN(code)) {
        verifyStatusEl.innerText = "?? Geçerli 6 haneli bir kod giriniz.";
        return;
    }

    //Get reCAPTCHA response
    const recaptchaResponse = grecaptcha.getResponse();

    if (!recaptchaResponse) {
        verifyStatusEl.innerText = "Lütfen reCAPTCHA'yı tamamlayın.";
        return;
    }

    verifyStatusEl.innerText = "Doğrulanıyor..."; //Show loading

    try {
        const formData = new FormData();
        formData.append("code", code);
        formData.append("recaptcha_response", recaptchaResponse); //Send reCAPTCHA response to backend

        const response = await fetch(API_ENDPOINT_VERIFY, {
            method: "POST",
            body: formData //Use FormData for reCAPTCHA
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === "success") {
            verifyStatusEl.innerText = "? Doğrulama başarılı! PioneerAI paneline yönlendiriliyorsunuz...";

            setTimeout(() => {
                window.location.href = DASHBOARD_URL;
            }, 2000);
        } else {
            verifyStatusEl.innerText = "? Kod hatalı! Lütfen tekrar deneyin."; //Generic message
        }
    } catch (error) {
        console.error("Sunucu hatası:", error);
        verifyStatusEl.innerText = "? Sunucuya erişilemiyor.";
    } finally {
        //Reset reCAPTCHA after each attempt
        grecaptcha.reset();
    }
}
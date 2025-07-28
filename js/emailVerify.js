// js/emailVerify.js
import { postJSON } from "./api.js";

const sendBtn    = document.getElementById("sendBtn");
const emailInput = document.getElementById("emailInput");
const statusEl   = document.getElementById("emailStatus");
const codeZone   = document.getElementById("codeZone");
const ENDPOINT   = "http://localhost:5000/send-code";

/**
 * E-posta formatını kontrol eder.
 * @param {string} email
 * @returns {string|null} Hata mesajı veya null
 */
function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email)              return "E-posta adresi boş bırakılamaz.";
  if (!regex.test(email))  return "Lütfen geçerli bir e-posta girin.";
  return null;
}

/**
 * Doğrulama kodu gönderme akışını yönetir.
 */
async function sendVerificationCode() {
  statusEl.textContent = "";
  codeZone.style.display = "none";

  const email = emailInput.value.trim();
  const error = validateEmail(email);
  if (error) {
    statusEl.textContent = error;
    return;
  }

  sendBtn.disabled      = true;
  statusEl.textContent  = "Kod gönderiliyor…";

  try {
    const data = await postJSON(ENDPOINT, { email }, 7000);
    if (data.status === "success") {
      statusEl.textContent = "✔ Kod gönderildi!";
      codeZone.style.display = "block";
    } else {
      statusEl.textContent = "✖ Kod gönderilemedi. Lütfen tekrar deneyin.";
    }
  } catch (err) {
    if (err.name === "AbortError") {
      statusEl.textContent = "⌛ İstek zaman aşımına uğradı.";
    } else {
      console.error("Sunucu hatası:", err);
      statusEl.textContent = "⚠ Sunucuya ulaşılamıyor.";
    }
  } finally {
    sendBtn.disabled = false;
  }
}

sendBtn.addEventListener("click", sendVerificationCode);

export { validateEmail, sendVerificationCode };
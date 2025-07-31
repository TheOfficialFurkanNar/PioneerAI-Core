// js/emailVerify.js (Refactored & Enhanced)
import { postJSON } from "./api.js";

const sendBtn    = document.getElementById("sendBtn");
const emailInput = document.getElementById("emailInput");
const statusEl   = document.getElementById("emailStatus");
const codeZone   = document.getElementById("codeZone");
const ENDPOINT   = "http://localhost:5000/send-code";

// Accessibility: Announce status updates
if (statusEl) statusEl.setAttribute("aria-live", "polite");

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
  if (!sendBtn || !emailInput || !statusEl || !codeZone) return; // Robustness

  statusEl.textContent = "";
  codeZone.style.display = "none";

  const email = emailInput.value.trim();
  const error = validateEmail(email);
  if (error) {
    statusEl.textContent = error;
    emailInput.focus();
    return;
  }

  sendBtn.disabled      = true;
  statusEl.textContent  = "Kod gönderiliyor…";

  try {
    const data = await postJSON(ENDPOINT, { email }, 7000);
    if (data.status === "success") {
      statusEl.textContent = "✔ Kod gönderildi!";
      codeZone.style.display = "block";
      // Optionally, focus first input in codeZone
      const codeInput = codeZone.querySelector("input");
      if (codeInput) codeInput.focus();
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

// Support pressing Enter to send
if (emailInput) {
  emailInput.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendVerificationCode();
    }
  });
}

if (sendBtn) sendBtn.addEventListener("click", sendVerificationCode);

export { validateEmail, sendVerificationCode };
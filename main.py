# main.py

import openai
import json, time, os
from datetime import datetime
from collections import deque

# proje kökünden import’lar
from config.settings import (
    OPENAI_API_KEY, SYSTEM_PROMPT, SESSION_TIMEOUT,
    LOG_FILE, MEMORY_JSON, MEMORY_TXT, MAX_TOKENS, TEMPERATURE,
    FREQUENCY_PENALTY, PRESENCE_PENALTY, TOP_P, ENCODING, ENSURE_ASCII
)
import tiktoken
from modules.task_router import classify_intent

# ✅ Ortam değişken kontrolü
openai.api_key = os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY
conversation_history = deque(maxlen=20)
last_input_time = time.time()

# 🔁 Hafızadan geçmişi geri çek (opsiyonel)
def load_memory():
    try:
        with open(MEMORY_JSON, "r", encoding=ENCODING) as f:
            data = json.load(f)
            for turn in data.get("conversation", []):
                conversation_history.append({
                    "user": turn["user"],
                    "bot": turn["bot"]
                })
    except Exception:
        pass

# 🧠 Token sayımı + model seçimi
def select_model(prompt: str) -> str:
    history_text = " ".join([t["user"] + t["bot"] for t in conversation_history])
    full_text = history_text + prompt
    enc = tiktoken.encoding_for_model("gpt-4o")
    tokens = len(enc.encode(full_text))
    return "gpt-4o" if tokens > 3000 else "gpt-3.5-turbo"

# 📋 Bellek ve log yazıcı
def update_memory(user_input, bot_response):
    turn = {
        "user": user_input,
        "bot": bot_response,
        "timestamp": datetime.now().isoformat()
    }

    try:
        with open(MEMORY_JSON, "r+", encoding=ENCODING) as f:
            data = json.load(f)
            data["conversation"].append(turn)
            f.seek(0)
            json.dump(data, f, ensure_ascii=ENSURE_ASCII, indent=4)
    except Exception:
        with open(MEMORY_JSON, "w", encoding=ENCODING) as f:
            json.dump({"conversation": [turn]}, f, ensure_ascii=ENSURE_ASCII, indent=4)

    with open(MEMORY_TXT, "a", encoding=ENCODING) as f:
        f.write(f"USER: {user_input}\nBOT : {bot_response}\n\n")

    conversation_history.append({"user": user_input, "bot": bot_response})

def log_interaction(user_input, bot_response):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding=ENCODING) as log_file:
        log_file.write(f"{timestamp} USER: {user_input}\n")
        log_file.write(f"{timestamp} BOT : {bot_response}\n\n")

# 💬 Ana GPT fonksiyonu
def chat_with_gpt(prompt):
    if prompt.startswith("!clear"):
        conversation_history.clear()
        print("🧼 Hafıza temizlendi.")
        return "Hafıza silindi."

    intent = classify_intent(prompt)
    model_name = select_model(prompt)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in conversation_history:
        messages.extend([
            {"role": "user", "content": turn["user"]},
            {"role": "assistant", "content": turn["bot"]}
        ])
    messages.append({"role": "user", "content": prompt})

    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY
        )
        output = response.choices[0].message.content.strip()
    except openai.error.AuthenticationError:
        output = "[API] Kimlik doğrulama hatası."
    except openai.error.RateLimitError:
        output = "[API] Limit aşıldı, bekleyin."
    except openai.error.Timeout:
        output = "[API] Zaman aşımı."
    except Exception as e:
        output = f"[HATA] Yanıt alınamadı: {str(e)}"

    log_interaction(prompt, output)
    update_memory(prompt, output)
    return output

# 🖥️ Terminal Arayüzü
if __name__ == "__main__":
    print("🧠 PioneerChat v0.4.0 başlatıldı – Streaming ve görev tanıma aktif.")
    load_memory()

    while True:
        if time.time() - last_input_time > SESSION_TIMEOUT:
            print("⏳ Oturum süresi doldu. Güvenlik nedeniyle çıkış yapılıyor.")
            break

        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\n🚪 Çıkış yapılıyor…")
            break

        last_input_time = time.time()

        if user_input.strip().lower() in ["quit", "exit", "bye"]:
            print("Chatbot: Görüşmek üzere komutan 🚀")
            break

        response = chat_with_gpt(user_input)
        print("Chatbot:", response)
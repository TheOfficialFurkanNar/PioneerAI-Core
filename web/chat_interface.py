# web/chat_interface.py

import os
import json
import time
import threading
import asyncio
from datetime import datetime

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv

from modules.orchestrator import handle_standard_message, handle_stream_message
from config.settings import MEMORY_JSON as MEMORY_PATH
from .auth_routes import auth_bp, token_required

import tiktoken

# 🧠 Ortam değişkenlerini yükle
load_dotenv()

# 🌐 Flask uygulaması
app = Flask(__name__)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = allowed_origins.split(",") if allowed_origins != "*" else "*"
CORS(app, origins=allowed_origins, supports_credentials=True)

# 🔐 Auth routes'ları kaydet
app.register_blueprint(auth_bp)

# 🔐 Dosya sistemi güvenliği
os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
os.makedirs("logs", exist_ok=True)
_lock = threading.Lock()

# 📏 Token hesaplayıcı
def count_tokens(text: str) -> int:
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# 💾 Hafıza kaydı
def save_to_memory(user_msg: str, bot_reply: str):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user_msg,
        "bot": bot_reply
    }
    with _lock:
        try:
            with open(MEMORY_PATH, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.append(entry)
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()
        except FileNotFoundError:
            with open(MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump([entry], f, ensure_ascii=False, indent=2)

# 📊 Performans log'u
def log_performance(reply: str, duration: float):
    token_count = count_tokens(reply)
    log_entry = f"{datetime.utcnow().isoformat()} | Duration: {duration:.2f}s | Tokens: {token_count}\n"
    with open("logs/performance.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

# ------------------------------------------------------------
# 🔹 Tek Yanıtlı Özet Endpoint'i (Kimlik doğrulama gerekli)
# ------------------------------------------------------------
@app.route("/ask/summary", methods=["POST"])
@token_required
def ask_summary(current_user):
    data = request.get_json()
    user_id = str(current_user.id)  # Authenticated user ID
    message = data.get("prompt", "")
    style = data.get("style", "brief")

    if not message:
        return jsonify({"error": True, "message": "prompt eksik"}), 400

    start_time = time.time()
    result = asyncio.run(handle_standard_message(user_id, message))
    duration = time.time() - start_time

    save_to_memory(message, result["reply"])
    log_performance(result["reply"], duration)

    return jsonify({
        "response": result["reply"],
        "meta": result["meta"]
    })

# ------------------------------------------------------------
# 🔸 Akışlı (stream) Özet Endpoint'i (Kimlik doğrulama gerekli)
# ------------------------------------------------------------
@app.route("/ask/summary/stream", methods=["POST"])
@token_required
def stream_summary(current_user):
    data = request.get_json()
    user_id = str(current_user.id)  # Authenticated user ID
    message = data.get("prompt", "")
    style = data.get("style", "brief")

    if not message:
        return jsonify({"error": True, "message": "prompt eksik"}), 400

    def generate():
        async def streamer():
            async for chunk in handle_stream_message(user_id, message, style):
                yield chunk.encode("utf-8")
        return asyncio.run(streamer())

    return Response(generate(), content_type="text/plain")

# 🟢 Sunucu başlatma
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT, debug=True)
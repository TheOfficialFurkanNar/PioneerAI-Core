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
from web.auth_routes import auth_bp, token_required
from web.database import init_database

import tiktoken

# 🧠 Ortam değişkenlerini yükle
load_dotenv()

# 🌐 Flask uygulaması
app = Flask(__name__)

# Production configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'pioneer-ai-secret-key-2024')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
cors_origins = os.getenv("CORS_ORIGINS", allowed_origins)
cors_origins = cors_origins.split(",") if cors_origins != "*" else "*"

<<<<<<< HEAD
CORS(app,
     origins=cors_origins,
=======
CORS(app,
     origins=cors_origins,
>>>>>>> 0285be0883ab9d10884b57d1097c61f567b39165
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# 🔐 Authentication blueprint'ini kaydet
app.register_blueprint(auth_bp, url_prefix='/auth')

# 🗄️ Veritabanını başlat
init_database()

# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers for production"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

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
# 🔹 Tek Yanıtlı Özet Endpoint'i
# ------------------------------------------------------------
@app.route("/ask/summary", methods=["POST"])
@token_required
def ask_summary():
    data = request.get_json()
    user_id = str(request.current_user['id'])  # JWT'den gelen kullanıcı ID'si
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
# 🔸 Akışlı (stream) Özet Endpoint'i
# ------------------------------------------------------------
@app.route("/ask/summary/stream", methods=["POST"])
@token_required
def stream_summary():
    data = request.get_json()
    user_id = str(request.current_user['id'])  # JWT'den gelen kullanıcı ID'si
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
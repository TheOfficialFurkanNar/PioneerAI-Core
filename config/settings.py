# config/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Proje kök dizinini belirle ve .env.safe dosyasını yükle
BASE_DIR = Path(__file__).parent.parent
ENV_PATH = BASE_DIR / ".env.safe"
load_dotenv(dotenv_path=ENV_PATH)

# 🌐 OpenAI Ayarları
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o")

# main.py ve diğer kodlarda kullanılan model adı
MODEL_NAME = os.getenv("MODEL_NAME") or OPENAI_MODEL

# Sistem prompt’u
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are PioneerChat, a thoughtful assistant."
)

# 🧠 Model parametreleri
MAX_TOKENS        = int(os.getenv("MAX_TOKENS", 500))
TEMPERATURE       = float(os.getenv("TEMPERATURE", 0.7))
TOP_P             = float(os.getenv("TOP_P", 1.0))
FREQUENCY_PENALTY = float(os.getenv("FREQUENCY_PENALTY", 0.0))
PRESENCE_PENALTY  = float(os.getenv("PRESENCE_PENALTY", 0.0))

# ⏳ Oturum zaman aşımı (saniye)
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 300))

# 📂 Dosya ve dizin yolları
LOG_DIR      = BASE_DIR / os.getenv("LOG_DIR", "logs")
LOG_FILE     = os.getenv("LOG_FILE", str(LOG_DIR / "pioneer.log"))

DATA_DIR     = BASE_DIR / os.getenv("DATA_DIR", "data")
MEMORY_JSON  = os.getenv("MEMORY_JSON", str(DATA_DIR / "memory.json"))
MEMORY_TXT   = os.getenv("MEMORY_TXT", str(DATA_DIR / "conversation_memory.txt"))

# 🗄️ Veritabanı ayarları
DB_DIR   = os.getenv("DB_DIR", str(DATA_DIR))
DB_NAME  = os.getenv("DB_NAME", "pioneer.db")
DB_PATH  = os.getenv("DB_PATH", str(Path(DB_DIR) / DB_NAME))

# 📝 Özetleme ve bağlam sınırları
SUMMARY_TIMEOUT     = int(os.getenv("SUMMARY_TIMEOUT", 15))
MAX_CONTEXT_TOKENS  = int(os.getenv("MAX_CONTEXT_TOKENS", 2000))

# 🧬 Metin encoding seçenekleri
ENCODING     = os.getenv("ENCODING", "utf-8")
ENSURE_ASCII = os.getenv("ENSURE_ASCII", "False").lower() == "true"

# 🧠 Attention Mechanism Configuration
ATTENTION_HEADS = int(os.getenv("ATTENTION_HEADS", 8))
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 512))
SEQUENCE_LENGTH = int(os.getenv("SEQUENCE_LENGTH", 1024))
DROPOUT_RATE = float(os.getenv("DROPOUT_RATE", 0.1))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", 0.0001))
NUM_ENCODER_LAYERS = int(os.getenv("NUM_ENCODER_LAYERS", 6))
NUM_DECODER_LAYERS = int(os.getenv("NUM_DECODER_LAYERS", 6))
PRE_TRAINED_EMBEDDINGS = os.getenv("PRE_TRAINED_EMBEDDINGS", "")
POSITIONAL_ENCODING_TYPE = os.getenv("POSITIONAL_ENCODING_TYPE", "fixed")
HYBRID_MODE_THRESHOLD = float(os.getenv("HYBRID_MODE_THRESHOLD", 0.8))
CACHE_SIZE = int(os.getenv("CACHE_SIZE", 1000))

# 🔄 Attention Processing Mode
ATTENTION_MODE = os.getenv("ATTENTION_MODE", "hybrid")  # "local", "openai", "hybrid"
ATTENTION_CACHE_ENABLED = os.getenv("ATTENTION_CACHE_ENABLED", "True").lower() == "true"

def get_model_name(fallback: str = "gpt-4o") -> str:
    """
    Dönülecek model adı:
      1. Ortam değişkeni MODEL_NAME
      2. Ortam değişkeni OPENAI_MODEL
      3. Fonksiyona verilen fallback
    """
    return os.getenv("MODEL_NAME") or os.getenv("OPENAI_MODEL") or fallback
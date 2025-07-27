# modules/memory_manager.py

import json
import os
import redis
from typing import List, Dict, Any

# Redis istemcisi
r = redis.Redis(host="localhost", port=6379, db=0)

def set_cache(key: str, value: Any) -> None:
    """
    Verilen anahtar-değer çiftini Redis'e kaydeder.
    """
    payload = json.dumps(value, ensure_ascii=False)
    r.set(key, payload)

def get_cache(key: str) -> Any:
    """
    Redis'ten değer okur, JSON formatında decode eder.
    Anahtar yoksa None döner.
    """
    raw = r.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def get_user_conversation(user_id: str) -> List[Dict[str, Any]]:
    """
    Kullanıcının önceki konuşma geçmişini önce Redis cache'inden
    dener, yoksa diskten okur ve cache'e yazar.
    """
    key = f"conversation_{user_id}"
    # 1) Önce Redis'ten oku
    cached = get_cache(key)
    if isinstance(cached, list):
        return cached

    # 2) Cache yoksa dosyadan oku
    path = f"memory/conversation_{user_id}.json"
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    # 3) Diskten okunanı cache'e kaydet
    set_cache(key, data)
    return data


async def set_user_conversation(user_id: str, conv: List[Dict[str, Any]]) -> None:
    """
    Kullanıcı konuşma geçmişini hem diskte hem de Redis cache'inde günceller.
    """
    # 1) Disk tarafı
    path = f"memory/conversation_{user_id}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(conv, f, ensure_ascii=False, indent=2)

    # 2) Cache tarafı
    set_cache(f"conversation_{user_id}", conv)
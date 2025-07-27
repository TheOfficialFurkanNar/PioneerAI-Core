# modules/engine.py

import os
import aiosqlite
from config.settings import DB_DIR, DB_PATH

async def get_connection() -> aiosqlite.Connection:
    """
    data/ dizinini oluşturur (varsa yeniden yaratmaz)
    ve pioneer.db’ye bağlanan asenkron bağlantıyı döner.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    return await aiosqlite.connect(DB_PATH)

async def init_database() -> None:
    """
    pioneer.db dosyasını oluşturur (yoksa) ve
    chat_log tablosunu tanımlar.
    """
    conn = await get_connection()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_log (
            user_id   TEXT,
            message   TEXT,
            timestamp REAL
        )
    """)
    await conn.commit()
    await conn.close()

if __name__ == "__main__":
    import asyncio
    # Veritabanı altyapısını bir kere başlat
    asyncio.run(init_database())
    print("✅ pioneer.db ve chat_log tablosu başarıyla oluşturuldu.")
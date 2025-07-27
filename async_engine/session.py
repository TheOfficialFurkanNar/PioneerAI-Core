# async_engine/session.py

from modules.engine import get_connection

async def fetch_latest_messages(user_id: str):
    conn = await get_connection()
    cursor = await conn.execute("SELECT message FROM chat_log WHERE user_id = ?", (user_id,))
    rows = await cursor.fetchall()
    await conn.close()
    return [row[0] for row in rows]
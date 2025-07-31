from modules.engine import get_connection

async def fetch_latest_messages(user_id: str, limit: int = 10):
    """
    Fetch the latest chat messages for a given user from the database.
    Args:
        user_id (str): The user's ID.
        limit (int): Maximum number of messages to fetch.
    Returns:
        List[str]: List of message strings.
    """
    try:
        conn = await get_connection()
        cursor = await conn.execute(
            "SELECT message FROM chat_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        # Log error or handle as needed
        print(f"Database fetch error: {e}")
        return []
    finally:
        if conn:
            await conn.close()
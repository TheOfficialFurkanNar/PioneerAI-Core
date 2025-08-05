# web/database.py

import sqlite3
import os
import bcrypt
from datetime import datetime
from typing import Optional, Dict, Any

DATABASE_PATH = "data/users.db"

<< << << < HEAD

== == == =
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def init_database():
    """Veritabanını başlat ve kullanıcı tablosunu oluştur"""
    # data dizinini oluştur
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

<< << << < HEAD

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

== == == =

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# Kullanıcı tablosunu oluştur
cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
<< << << < HEAD

conn.commit()
conn.close()

== == == =

conn.commit()
conn.close()

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def hash_password(password: str) -> str:
    """Şifreyi hash'le"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

<< << << < HEAD

== == == =
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def verify_password(password: str, hashed: str) -> bool:
    """Şifreyi doğrula"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

<< << << < HEAD

== == == =
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def create_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """Yeni kullanıcı oluştur"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# Kullanıcı adı ve email kontrolü
cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
if cursor.fetchone():
    return {"success": False, "message": "Kullanıcı adı veya email zaten kullanımda"}
<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# Şifreyi hash'le ve kullanıcıyı oluştur
password_hash = hash_password(password)
cursor.execute(
    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
    (username, email, password_hash)
)
<< << << < HEAD

user_id = cursor.lastrowid
conn.commit()
conn.close()

return {
    "success": True,
    "message": "Kullanıcı başarıyla oluşturuldu",
    "user_id": user_id
}

except sqlite3.Error as e:
return {"success": False, "message": f"Veritabanı hatası: {str(e)}"}

== == == =

user_id = cursor.lastrowid
conn.commit()
conn.close()

return {
    "success": True,
    "message": "Kullanıcı başarıyla oluşturuldu",
    "user_id": user_id
}

except sqlite3.Error as e:
return {"success": False, "message": f"Veritabanı hatası: {str(e)}"}

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """Kullanıcı kimlik doğrulaması"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
cursor.execute(
    "SELECT id, username, email, password_hash FROM users WHERE username = ?",
    (username,)
)
user = cursor.fetchone()
<< << << < HEAD

if not user:
    return {"success": False, "message": "Kullanıcı bulunamadı"}

user_id, username, email, password_hash = user

if not verify_password(password, password_hash):
    return {"success": False, "message": "Geçersiz şifre"}

== == == =

if not user:
    return {"success": False, "message": "Kullanıcı bulunamadı"}

user_id, username, email, password_hash = user

if not verify_password(password, password_hash):
    return {"success": False, "message": "Geçersiz şifre"}

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# Son giriş zamanını güncelle
cursor.execute(
    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
    (user_id,)
)
conn.commit()
conn.close()
<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
return {
    "success": True,
    "message": "Giriş başarılı",
    "user": {
        "id": user_id,
        "username": username,
        "email": email
    }
}
<< << << < HEAD

except sqlite3.Error as e:
return {"success": False, "message": f"Veritabanı hatası: {str(e)}"}

== == == =

except sqlite3.Error as e:
return {"success": False, "message": f"Veritabanı hatası: {str(e)}"}

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """ID ile kullanıcı bilgilerini getir"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
cursor.execute(
    "SELECT id, username, email, created_at, last_login FROM users WHERE id = ?",
    (user_id,)
)
user = cursor.fetchone()
conn.close()
<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
if user:
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "created_at": user[3],
        "last_login": user[4]
    }
return None
<< << << < HEAD

except sqlite3.Error:
return None

== == == =

except sqlite3.Error:
return None

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def validate_username(username: str) -> Dict[str, Any]:
    """Kullanıcı adı doğrulaması"""
    if not username:
        return {"valid": False, "message": "Kullanıcı adı boş olamaz"}
    if len(username) < 3:
        return {"valid": False, "message": "Kullanıcı adı en az 3 karakter olmalıdır"}
    if len(username) > 20:
        return {"valid": False, "message": "Kullanıcı adı en fazla 20 karakter olabilir"}
    if not username.replace("_", "").replace("-", "").isalnum():
        return {"valid": False, "message": "Kullanıcı adı sadece harf, rakam, _ ve - içerebilir"}
    return {"valid": True}

<< << << < HEAD

== == == =
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def validate_email(email: str) -> Dict[str, Any]:
    """Email doğrulaması"""
    import re
    if not email:
        return {"valid": False, "message": "Email boş olamaz"}

<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
if not re.match(email_pattern, email):
    return {"valid": False, "message": "Geçersiz email formatı"}
return {"valid": True}

<< << << < HEAD

== == == =
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def validate_password(password: str) -> Dict[str, Any]:
    """Şifre doğrulaması"""
    if not password:
        return {"valid": False, "message": "Şifre boş olamaz"}
    if len(password) < 8:
        return {"valid": False, "message": "Şifre en az 8 karakter olmalıdır"}
    return {"valid": True}

<< << << < HEAD

== == == =
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def test_database_connection() -> bool:
    """Test database connection and basic functionality"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        cursor.fetchone()
        conn.close()
        return True
    except sqlite3.Error:
        return False
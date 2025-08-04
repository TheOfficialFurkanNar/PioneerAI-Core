# web/database.py

import sqlite3
import bcrypt
import os
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager

# 🗄️ Veritabanı dosya yolu
DB_PATH = os.path.join("data", "users.db")

class User:
    """Kullanıcı modeli"""
    def __init__(self, id: int = None, username: str = None, email: str = None, 
                 password_hash: str = None, created_at: str = None, last_login: str = None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.last_login = last_login

    def to_dict(self) -> Dict[str, Any]:
        """Kullanıcı bilgilerini dict olarak döndür (şifre hariç)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "last_login": self.last_login
        }

@contextmanager
def get_db_connection():
    """Veritabanı bağlantısı context manager'ı"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Dict-like access
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Veritabanını başlat ve users tablosunu oluştur"""
    # Veri dizinini oluştur
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        ''')
        conn.commit()

def hash_password(password: str) -> str:
    """Şifreyi hash'le"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Şifreyi doğrula"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_user(username: str, email: str, password: str) -> Optional[User]:
    """Yeni kullanıcı oluştur"""
    try:
        password_hash = hash_password(password)
        created_at = datetime.utcnow().isoformat()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, created_at))
            conn.commit()
            
            user_id = cursor.lastrowid
            return User(id=user_id, username=username, email=email, 
                       password_hash=password_hash, created_at=created_at)
    except sqlite3.IntegrityError:
        return None  # Kullanıcı adı veya email zaten mevcut

def get_user_by_username(username: str) -> Optional[User]:
    """Kullanıcı adına göre kullanıcı getir"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash'],
                created_at=row['created_at'],
                last_login=row['last_login']
            )
        return None

def get_user_by_email(email: str) -> Optional[User]:
    """Email'e göre kullanıcı getir"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash'],
                created_at=row['created_at'],
                last_login=row['last_login']
            )
        return None

def get_user_by_id(user_id: int) -> Optional[User]:
    """ID'ye göre kullanıcı getir"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash'],
                created_at=row['created_at'],
                last_login=row['last_login']
            )
        return None

def update_last_login(user_id: int):
    """Son giriş zamanını güncelle"""
    last_login = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (last_login, user_id))
        conn.commit()

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Kullanıcı kimlik doğrulaması"""
    user = get_user_by_username(username)
    if user and verify_password(password, user.password_hash):
        update_last_login(user.id)
        return user
    return None

# Veritabanını başlat
init_database()
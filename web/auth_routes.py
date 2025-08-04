# web/auth_routes.py

import os
import jwt
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from dotenv import load_dotenv

from .database import create_user, authenticate_user, get_user_by_id

# 🧠 Ortam değişkenlerini yükle
load_dotenv()

# 🔐 JWT ayarları
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# 🌐 Blueprint oluştur
auth_bp = Blueprint('auth', __name__)

def validate_email(email: str) -> bool:
    """Email formatını doğrula"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username: str) -> bool:
    """Kullanıcı adı formatını doğrula"""
    # 3-20 karakter, sadece harf, rakam ve alt çizgi
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def validate_password(password: str) -> bool:
    """Şifre formatını doğrula"""
    # En az 8 karakter
    return len(password) >= 8

def generate_jwt_token(user_id: int) -> str:
    """JWT token oluştur"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    """JWT token'ı çöz"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """JWT token gerektiren endpoint'ler için decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Authorization header'dan token al
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer TOKEN"
            except IndexError:
                return jsonify({'error': 'Geçersiz token formatı'}), 401
        
        if not token:
            return jsonify({'error': 'Token eksik'}), 401
        
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Geçersiz veya süresi dolmuş token'}), 401
        
        current_user = get_user_by_id(payload['user_id'])
        if not current_user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """Kullanıcı kaydı"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON verisi eksik'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Veri doğrulama
        if not username or not email or not password:
            return jsonify({'error': 'Tüm alanlar zorunludur'}), 400
        
        if not validate_username(username):
            return jsonify({'error': 'Kullanıcı adı 3-20 karakter olmalı ve sadece harf, rakam, alt çizgi içermelidir'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Geçersiz email formatı'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Şifre en az 8 karakter olmalıdır'}), 400
        
        # Kullanıcı oluştur
        user = create_user(username, email, password)
        
        if not user:
            return jsonify({'error': 'Bu kullanıcı adı veya email zaten kullanımda'}), 409
        
        # JWT token oluştur
        token = generate_jwt_token(user.id)
        
        return jsonify({
            'message': 'Kayıt başarılı',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Kayıt hatası: {str(e)}")
        return jsonify({'error': 'Sunucu hatası'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı girişi"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON verisi eksik'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Kullanıcı adı ve şifre gereklidir'}), 400
        
        # Kullanıcı kimlik doğrulaması
        user = authenticate_user(username, password)
        
        if not user:
            return jsonify({'error': 'Kullanıcı adı veya şifre hatalı'}), 401
        
        # JWT token oluştur
        token = generate_jwt_token(user.id)
        
        return jsonify({
            'message': 'Giriş başarılı',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Giriş hatası: {str(e)}")
        return jsonify({'error': 'Sunucu hatası'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Kullanıcı çıkışı"""
    # JWT token'lar stateless olduğu için sunucu tarafında logout işlemi
    # genellikle client tarafında token'ı silmekle yapılır.
    # Burada sadece başarılı response döndürüyoruz.
    return jsonify({'message': 'Çıkış başarılı'}), 200

@auth_bp.route('/userinfo', methods=['POST'])
@token_required
def get_user_info(current_user):
    """Kullanıcı bilgilerini getir"""
    return jsonify({
        'user': current_user.to_dict()
    }), 200

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Token doğrulama endpoint'i"""
    try:
        data = request.get_json()
        token = data.get('token') if data else None
        
        if not token:
            return jsonify({'valid': False, 'error': 'Token eksik'}), 400
        
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({'valid': False, 'error': 'Geçersiz token'}), 401
        
        user = get_user_by_id(payload['user_id'])
        if not user:
            return jsonify({'valid': False, 'error': 'Kullanıcı bulunamadı'}), 401
        
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token doğrulama hatası: {str(e)}")
        return jsonify({'valid': False, 'error': 'Sunucu hatası'}), 500
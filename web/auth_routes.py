import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app

from .database import (
    create_user, authenticate_user, get_user_by_id,
    validate_username, validate_email, validate_password
)

# JWT secret key - environment variable ile veya fallback
JWT_SECRET = os.getenv('JWT_SECRET', 'pioneer-ai-secret-key-2024')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Blueprint oluştur
auth_bp = Blueprint('auth', __name__)

<< << << < HEAD

== == == =
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def generate_token(user_id: int) -> str:
    """JWT token oluştur"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

<< << << < HEAD

== == == =
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


def decode_token(token: str) -> dict:
    """JWT token çöz"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"success": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": "Token süresi dolmuş"}
    except jwt.InvalidTokenError:
        return {"success": False, "message": "Geçersiz token"}

<< << << < HEAD


def token_required(f):
    """Token gerektiren endpoint'ler için decorator"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

== == == =

def token_required(f):
    """Token gerektiren endpoint'ler için decorator"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# Authorization header'dan token al
if 'Authorization' in request.headers:
    auth_header = request.headers['Authorization']
    try:
        token = auth_header.split(" ")[1]  # "Bearer TOKEN" formatı
    except IndexError:
        return jsonify({'error': True, 'message': 'Geçersiz token formatı'}), 401
<< << << < HEAD

if not token:
    return jsonify({'error': True, 'message': 'Token eksik'}), 401

== == == =

if not token:
    return jsonify({'error': True, 'message': 'Token eksik'}), 401

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# Token'ı doğrula
result = decode_token(token)
if not result["success"]:
    return jsonify({'error': True, 'message': result["message"]}), 401
<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# Kullanıcı bilgilerini request'e ekle
current_user = get_user_by_id(result["payload"]["user_id"])
if not current_user:
    return jsonify({'error': True, 'message': 'Kullanıcı bulunamadı'}), 401
<< << << < HEAD

request.current_user = current_user
return f(*args, **kwargs)

return decorated

== == == =

request.current_user = current_user
return f(*args, **kwargs)

return decorated

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


@auth_bp.route('/register', methods=['POST'])
def register():
    """Kullanıcı kayıt endpoint'i"""
    try:
        data = request.get_json()

<< << << < HEAD

if not data:
    return jsonify({'error': True, 'message': 'Veri eksik'}), 400

username = data.get('username', '').strip()
email = data.get('email', '').strip()
password = data.get('password', '')

== == == =

if not data:
    return jsonify({'error': True, 'message': 'Veri eksik'}), 400

username = data.get('username', '').strip()
email = data.get('email', '').strip()
password = data.get('password', '')

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
# Input validation
username_validation = validate_username(username)
if not username_validation["valid"]:
    return jsonify({'error': True, 'message': username_validation["message"]}), 400
<< << << < HEAD

email_validation = validate_email(email)
if not email_validation["valid"]:
    return jsonify({'error': True, 'message': email_validation["message"]}), 400

password_validation = validate_password(password)
if not password_validation["valid"]:
    return jsonify({'error': True, 'message': password_validation["message"]}), 400

# Kullanıcı oluştur
result = create_user(username, email, password)

== == == =

email_validation = validate_email(email)
if not email_validation["valid"]:
    return jsonify({'error': True, 'message': email_validation["message"]}), 400

password_validation = validate_password(password)
if not password_validation["valid"]:
    return jsonify({'error': True, 'message': password_validation["message"]}), 400

# Kullanıcı oluştur
result = create_user(username, email, password)

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
if result["success"]:
    # Token oluştur
    token = generate_token(result["user_id"])
    return jsonify({
        'success': True,
        'message': result["message"],
        'token': token,
        'user': {
            'id': result["user_id"],
            'username': username,
            'email': email
        }
    }), 201
else:
    return jsonify({'error': True, 'message': result["message"]}), 400
<< << << < HEAD

except Exception as e:
return jsonify({'error': True, 'message': f'Sunucu hatası: {str(e)}'}), 500

== == == =

except Exception as e:
return jsonify({'error': True, 'message': f'Sunucu hatası: {str(e)}'}), 500

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı giriş endpoint'i"""
    try:
        data = request.get_json()

<< << << < HEAD

if not data:
    return jsonify({'error': True, 'message': 'Veri eksik'}), 400

username = data.get('username', '').strip()
password = data.get('password', '')

if not username or not password:
    return jsonify({'error': True, 'message': 'Kullanıcı adı ve şifre gerekli'}), 400

# Kullanıcı doğrulama
result = authenticate_user(username, password)

== == == =

if not data:
    return jsonify({'error': True, 'message': 'Veri eksik'}), 400

username = data.get('username', '').strip()
password = data.get('password', '')

if not username or not password:
    return jsonify({'error': True, 'message': 'Kullanıcı adı ve şifre gerekli'}), 400

# Kullanıcı doğrulama
result = authenticate_user(username, password)

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
if result["success"]:
    # Token oluştur
    token = generate_token(result["user"]["id"])
    return jsonify({
        'success': True,
        'message': result["message"],
        'token': token,
        'user': result["user"]
    }), 200
else:
    return jsonify({'error': True, 'message': result["message"]}), 401
<< << << < HEAD

except Exception as e:
return jsonify({'error': True, 'message': f'Sunucu hatası: {str(e)}'}), 500

== == == =

except Exception as e:
return jsonify({'error': True, 'message': f'Sunucu hatası: {str(e)}'}), 500

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Kullanıcı çıkış endpoint'i"""
    # JWT stateless olduğu için sadece başarı mesajı döndür
    # Client-side'da token'ı silmek gerekir
    return jsonify({
        'success': True,
        'message': 'Başarıyla çıkış yapıldı'
    }), 200

<< << << < HEAD

== == == =
>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


@auth_bp.route('/userinfo', methods=['GET'])
@token_required
def get_user_info():
    """Kullanıcı bilgileri endpoint'i"""
    try:
        user = request.current_user
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'],
                'last_login': user['last_login']
            }
        }), 200

<< << << < HEAD

except Exception as e:
return jsonify({'error': True, 'message': f'Sunucu hatası: {str(e)}'}), 500

== == == =

except Exception as e:
return jsonify({'error': True, 'message': f'Sunucu hatası: {str(e)}'}), 500

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Token doğrulama endpoint'i"""
    try:
        data = request.get_json()

<< << << < HEAD

if not data or 'token' not in data:
    return jsonify({'error': True, 'message': 'Token eksik'}), 400

token = data['token']
result = decode_token(token)

== == == =

if not data or 'token' not in data:
    return jsonify({'error': True, 'message': 'Token eksik'}), 400

token = data['token']
result = decode_token(token)

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
if result["success"]:
    # Kullanıcı bilgilerini getir
    user = get_user_by_id(result["payload"]["user_id"])
    if user:
        return jsonify({
            'success': True,
            'message': 'Token geçerli',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200
    else:
        return jsonify({'error': True, 'message': 'Kullanıcı bulunamadı'}), 401
else:
    return jsonify({'error': True, 'message': result["message"]}), 401
<< << << < HEAD

== == == =

>> >> >> > 02
85
be0883ab9d10884b57d1097c61f567b39165
except Exception as e:
return jsonify({'error': True, 'message': f'Sunucu hatası: {str(e)}'}), 500
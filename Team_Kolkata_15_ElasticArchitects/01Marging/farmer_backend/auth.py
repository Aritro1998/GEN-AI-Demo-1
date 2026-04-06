# Authentication Logic

import jwt
import datetime
from passlib.hash import argon2
from fastapi import HTTPException, status, Header
from typing import Optional

class AuthManager:
    def __init__(self, secret, algorithm):
        self.secret = secret
        self.algorithm = algorithm
    
    def hash_password(self, password):
        return argon2.hash(password)
    
    def verify_password(self, password, hashed):
        try:
            return argon2.verify(password, hashed)
        except Exception:
            return False
    
    def create_jwt(self, user_id, username, user_role, exp_minutes=1440):  # Extended to 24 hours
        payload = {
            'user_id': user_id,
            'username': username,
            'role': user_role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=exp_minutes)
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def decode_jwt(self, token):
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

# Helper functions for authentication and authorization
def authenticate_token(auth_manager, x_access_token: str = Header(...)):
    """Extract and validate token, return payload"""
    try:
        payload = auth_manager.decode_jwt(x_access_token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

def require_role(required_roles: list[str]):
    """Decorator factory for role-based access control"""
    def role_checker(x_access_token: str = Header(...)):
        from main import auth_manager  # Import from main
        payload = authenticate_token(auth_manager, x_access_token)
        user_role = payload.get('role')
        
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {required_roles}"
            )
        return payload
    return role_checker

# Role dependency shortcuts
def require_farmer_or_admin(x_access_token: str = Header(...)):
    """Allow both farmers and admins"""
    from main import auth_manager
    payload = authenticate_token(auth_manager, x_access_token)
    if payload.get('role') not in ['farmer', 'admin']:
        raise HTTPException(status_code=403, detail="Access denied")
    return payload

def require_admin_only(x_access_token: str = Header(...)):
    """Admin-only access"""
    from main import auth_manager
    payload = authenticate_token(auth_manager, x_access_token)
    if payload.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload
# repository/user_repository.py
"""
User authentication and management repository.
Handles all user-related database operations for the Plant Disease Detection System.
"""

import sqlite3
import datetime
import json
import os
from typing import Optional, Tuple, List, Dict
from contextlib import contextmanager
from auth import AuthManager

# --- Configuration Loading ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config.json')

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    DB_PATH = config.get('DB_PATH', 'plant_disease.db')
    JWT_SECRET = config.get('JWT_SECRET', 'secret-key')
    JWT_ALGORITHM = config.get('JWT_ALGORITHM', 'HS256')
else:
    DB_PATH = os.getenv('DB_PATH', 'plant_disease.db')
    JWT_SECRET = os.getenv('JWT_SECRET', 'secret-key')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

# Initialize auth manager
auth_manager = AuthManager(JWT_SECRET, JWT_ALGORITHM)


class UserRepository:
    """Repository for user management operations"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_user(self, username: str) -> Optional[sqlite3.Row]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
        
        Returns:
            User row if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            return cursor.fetchone()
    
    def get_user_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
        
        Returns:
            User row if found, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
            return cursor.fetchone()
    
    def create_user(
        self, 
        username: str, 
        password: str, 
        firstname: str,  # Fixed typo
        lastname: str, 
        created_by: str, 
        user_role: str = "farmer",
        location: Optional[str] = None,
        phone: Optional[str] = None
    ):
        """
        Create a new user.
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            firstname: User's first name
            lastname: User's last name
            created_by: Username of creator
            user_role: Role (farmer or admin)
            location: Optional location
            phone: Optional phone number
        
        Returns:
            ID of created user
        
        Raises:
            sqlite3.IntegrityError: If username already exists
        """
        hashed_pwd = auth_manager.hash_password(password)
        now = datetime.datetime.utcnow()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (
                    username, password_hash, firstname, lastname, 
                    user_role, created_by, location, phone, 
                    created_at, is_active, failed_login_attempts
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """, (
                username, hashed_pwd, firstname, lastname, 
                user_role, created_by, location, phone, now
            ))
            conn.commit()
    
    def delete_user(self, username: str) -> bool:
        """
        Delete a user (soft delete by setting is_active=0).
        
        Args:
            username: Username to delete
        
        Returns:
            True if user was deleted, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Use soft delete instead of hard delete
            cursor.execute(
                "UPDATE users SET is_active=0 WHERE username=?", 
                (username,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def hard_delete_user(self, username: str) -> bool:
        """
        Permanently delete a user from database.
        
        Args:
            username: Username to delete
        
        Returns:
            True if user was deleted, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            return cursor.rowcount > 0
    
    def unlock_user(self, username: str) -> bool:
        """
        Unlock a locked user account.
        
        Args:
            username: Username to unlock
        
        Returns:
            True if user was unlocked, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET is_active=1, failed_login_attempts=0 
                WHERE username=?
            """, (username,))
            conn.commit()
            return cursor.rowcount > 0
    
    def lock_user(self, username: str) -> bool:
        """
        Lock a user account.
        
        Args:
            username: Username to lock
        
        Returns:
            True if user was locked, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET is_active=0 
                WHERE username=?
            """, (username,))
            conn.commit()
            return cursor.rowcount > 0
    
    def change_password(self, username: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            username: Username
            new_password: New plain text password (will be hashed)
        
        Returns:
            True if password was changed, False if user not found
        """
        hashed_pwd = auth_manager.hash_password(new_password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET password_hash=? 
                WHERE username=?
            """, (hashed_pwd, username))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_user_profile(
        self,
        username: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        location: Optional[str] = None,
        phone: Optional[str] = None
    ) -> bool:
        """
        Update user profile information.
        
        Args:
            username: Username to update
            firstname: New first name (optional)
            lastname: New last name (optional)
            location: New location (optional)
            phone: New phone (optional)
        
        Returns:
            True if user was updated, False if not found
        """
        updates = []
        params = []
        
        if firstname:
            updates.append("firstname=?")
            params.append(firstname)
        if lastname:
            updates.append("lastname=?")
            params.append(lastname)
        if location:
            updates.append("location=?")
            params.append(location)
        if phone:
            updates.append("phone=?")
            params.append(phone)
        
        if not updates:
            return False
        
        params.append(username)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE users SET {', '.join(updates)} WHERE username=?"
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def login(self, username: str, password: str) -> Tuple[Optional[str], str]:
        """
        Authenticate user and generate JWT token.
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            Tuple of (token, role) on success
            Tuple of (None, error_message) on failure
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get user information
            cursor.execute("""
                SELECT id, password_hash, is_active, user_role, failed_login_attempts 
                FROM users 
                WHERE username=?
            """, (username,))
            
            user = cursor.fetchone()
            
            if not user:
                return None, 'User not found'
            
            user_id = user['id']
            stored_hash = user['password_hash']
            is_active = user['is_active']
            user_role = user['user_role']
            failed_attempts = user['failed_login_attempts'] or 0
            
            # Check if account is locked
            if not is_active:
                return None, 'Account is locked. Contact administrator.'
            
            # Verify password
            if not auth_manager.verify_password(password, stored_hash):
                failed_attempts += 1
                
                if failed_attempts >= 3:
                    # Lock account after 3 failed attempts
                    cursor.execute("""
                        UPDATE users 
                        SET is_active=0, failed_login_attempts=? 
                        WHERE username=?
                    """, (failed_attempts, username))
                    conn.commit()
                    return None, 'Account locked due to too many failed attempts. Contact administrator.'
                else:
                    # Increment failed attempts
                    cursor.execute("""
                        UPDATE users 
                        SET failed_login_attempts=? 
                        WHERE username=?
                    """, (failed_attempts, username))
                    conn.commit()
                    remaining = 3 - failed_attempts
                    return None, f'Wrong password. {remaining} attempt(s) remaining.'
            
            # Successful login - reset failed attempts
            cursor.execute("""
                UPDATE users 
                SET failed_login_attempts=0 
                WHERE username=?
            """, (username,))
            conn.commit()
            
            # Generate JWT token (24 hours expiry)
            token = auth_manager.create_jwt(
                user_id, username, user_role, exp_minutes=1440
            )
            
            return token, user_role
    
    def get_all_users(self) -> List[Dict]:
        """
        Get all users in the system.
        
        Returns:
            List of user dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, username, firstname, lastname, user_role, 
                    created_by, created_at, location, phone, is_active, 
                    failed_login_attempts
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = cursor.fetchall()
            
            # Convert to list of dictionaries
            return [
                {
                    "id": u['id'],
                    "username": u['username'],
                    "firstname": u['firstname'],
                    "lastname": u['lastname'],
                    "user_role": u['user_role'],
                    "created_by": u['created_by'],
                    "created_at": u['created_at'],
                    "location": u['location'],
                    "phone": u['phone'],
                    "is_active": bool(u['is_active']),
                    "failed_login_attempts": u['failed_login_attempts']
                }
                for u in users
            ]
    
    def get_active_users(self) -> List[Dict]:
        """Get only active users"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, username, firstname, lastname, user_role, 
                    location, phone
                FROM users
                WHERE is_active=1
                ORDER BY username
            """)
            
            users = cursor.fetchall()
            
            return [
                {
                    "id": u['id'],
                    "username": u['username'],
                    "firstname": u['firstname'],
                    "lastname": u['lastname'],
                    "user_role": u['user_role'],
                    "location": u['location'],
                    "phone": u['phone']
                }
                for u in users
            ]
    
    def get_users_by_role(self, role: str) -> List[Dict]:
        """
        Get all users with specific role.
        
        Args:
            role: User role (farmer or admin)
        
        Returns:
            List of user dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, username, firstname, lastname, location, 
                    phone, is_active
                FROM users
                WHERE user_role=?
                ORDER BY username
            """, (role,))
            
            users = cursor.fetchall()
            
            return [
                {
                    "id": u['id'],
                    "username": u['username'],
                    "firstname": u['firstname'],
                    "lastname": u['lastname'],
                    "location": u['location'],
                    "phone": u['phone'],
                    "is_active": bool(u['is_active'])
                }
                for u in users
            ]
    
    def user_exists(self, username: str) -> bool:
        """
        Check if username exists.
        
        Args:
            username: Username to check
        
        Returns:
            True if exists, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM users WHERE username=?", 
                (username,)
            )
            result = cursor.fetchone()
            return result['count'] > 0
    
    def get_user_statistics(self) -> Dict:
        """
        Get user statistics.
        
        Returns:
            Dictionary with user counts
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total = cursor.fetchone()['count']
            
            # Active users
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active=1")
            active = cursor.fetchone()['count']
            
            # Farmers
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_role='farmer'")
            farmers = cursor.fetchone()['count']
            
            # Admins
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_role='admin'")
            admins = cursor.fetchone()['count']
            
            # Locked accounts
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active=0")
            locked = cursor.fetchone()['count']
            
            return {
                "total_users": total,
                "active_users": active,
                "locked_users": locked,
                "farmers": farmers,
                "admins": admins
            }

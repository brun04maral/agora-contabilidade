"""
Authentication logic for user login, logout, and session management
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt
import os
from sqlalchemy.orm import Session
from database.models.user import User


class AuthManager:
    """
    Manages user authentication and session tokens
    """

    def __init__(self, db_session: Session, secret_key: Optional[str] = None):
        """
        Initialize AuthManager

        Args:
            db_session: SQLAlchemy database session
            secret_key: Secret key for JWT encoding (defaults to env variable)
        """
        self.db_session = db_session
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'default-secret-key-change-in-production')
        self.token_expiry_hours = int(os.getenv('SESSION_EXPIRY_HOURS', '24'))

    def login(self, email: str, password: str) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Authenticate user with email and password

        Args:
            email: User's email
            password: User's password (plain text)

        Returns:
            Tuple of (success: bool, token: str or None, user_data: dict or None)
        """
        try:
            # Find user by email
            user = self.db_session.query(User).filter(User.email == email).first()

            if not user:
                return False, None, None

            # Check if user is active
            if not user.is_active:
                return False, None, None

            # Verify password
            if not user.check_password(password):
                return False, None, None

            # Update last login
            user.last_login = datetime.utcnow()
            self.db_session.commit()

            # Generate JWT token
            token = self._generate_token(user)

            return True, token, user.to_dict()

        except Exception as e:
            print(f"Login error: {e}")
            return False, None, None

    def verify_token(self, token: str) -> Tuple[bool, Optional[dict]]:
        """
        Verify JWT token and return user data

        Args:
            token: JWT token string

        Returns:
            Tuple of (valid: bool, user_data: dict or None)
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])

            # Check expiration
            exp = payload.get('exp')
            if exp and datetime.utcnow().timestamp() > exp:
                return False, None

            # Get user from database
            user_id = payload.get('user_id')
            user = self.db_session.query(User).filter(User.id == user_id).first()

            if not user or not user.is_active:
                return False, None

            return True, user.to_dict()

        except jwt.ExpiredSignatureError:
            return False, None
        except jwt.InvalidTokenError:
            return False, None
        except Exception as e:
            print(f"Token verification error: {e}")
            return False, None

    def _generate_token(self, user: User) -> str:
        """
        Generate JWT token for user

        Args:
            user: User object

        Returns:
            JWT token string
        """
        expiration = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)

        payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'exp': expiration.timestamp(),
            'iat': datetime.utcnow().timestamp()
        }

        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    def create_user(self, email: str, password: str, name: str, role: str = 'viewer') -> Tuple[bool, Optional[User]]:
        """
        Create a new user

        Args:
            email: User's email
            password: User's password (plain text)
            name: User's full name
            role: User's role (admin, socio, accountant, viewer)

        Returns:
            Tuple of (success: bool, user: User or None)
        """
        try:
            # Check if user already exists
            existing_user = self.db_session.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"User with email {email} already exists")
                return False, None

            # Create new user
            user = User(
                email=email,
                name=name,
                role=role
            )
            user.set_password(password)

            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)

            return True, user

        except Exception as e:
            self.db_session.rollback()
            print(f"User creation error: {e}")
            return False, None

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user's password

        Args:
            user_id: User's ID
            old_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully, False otherwise
        """
        try:
            user = self.db_session.query(User).filter(User.id == user_id).first()

            if not user:
                return False

            # Verify old password
            if not user.check_password(old_password):
                return False

            # Set new password
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            self.db_session.commit()

            return True

        except Exception as e:
            self.db_session.rollback()
            print(f"Password change error: {e}")
            return False

    def logout(self) -> bool:
        """
        Logout user (token invalidation is handled client-side by removing token)

        Returns:
            True
        """
        # For desktop app, logout is mainly handled by clearing the session file
        # Server-side token invalidation would require a blacklist (future enhancement)
        return True

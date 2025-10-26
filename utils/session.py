"""
Session management for desktop application
Handles local storage of authentication tokens
"""
import os
import json
from typing import Optional
from pathlib import Path


class SessionManager:
    """
    Manages user session storage for desktop application
    Stores authentication token in a local file
    """

    def __init__(self, session_file: Optional[str] = None):
        """
        Initialize SessionManager

        Args:
            session_file: Path to session file (defaults to .session in app directory)
        """
        if session_file:
            self.session_file = Path(session_file)
        else:
            # Store session file in user's home directory for persistence
            app_dir = Path.home() / '.agora_contabilidade'
            app_dir.mkdir(exist_ok=True)
            self.session_file = app_dir / 'session.json'

    def save_session(self, token: str, user_data: dict) -> bool:
        """
        Save session token and user data to file

        Args:
            token: JWT token string
            user_data: User information dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            session_data = {
                'token': token,
                'user': user_data
            }

            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

            # Set file permissions to user-only (600)
            os.chmod(self.session_file, 0o600)

            return True

        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def load_session(self) -> Optional[tuple]:
        """
        Load session token and user data from file

        Returns:
            Tuple of (token: str, user_data: dict) if session exists, None otherwise
        """
        try:
            if not self.session_file.exists():
                return None

            with open(self.session_file, 'r') as f:
                session_data = json.load(f)

            token = session_data.get('token')
            user_data = session_data.get('user')

            if token and user_data:
                return token, user_data

            return None

        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    def clear_session(self) -> bool:
        """
        Clear session by deleting session file

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            return True

        except Exception as e:
            print(f"Error clearing session: {e}")
            return False

    def has_session(self) -> bool:
        """
        Check if a session file exists

        Returns:
            True if session file exists, False otherwise
        """
        return self.session_file.exists()

    def get_user_data(self) -> Optional[dict]:
        """
        Get user data from current session

        Returns:
            User data dictionary if session exists, None otherwise
        """
        session = self.load_session()
        if session:
            _, user_data = session
            return user_data
        return None

    def get_token(self) -> Optional[str]:
        """
        Get authentication token from current session

        Returns:
            Token string if session exists, None otherwise
        """
        session = self.load_session()
        if session:
            token, _ = session
            return token
        return None

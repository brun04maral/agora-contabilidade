# -*- coding: utf-8 -*-
"""
Agora Media Production - Sistema de Contabilidade
Ponto de entrada principal da aplicação
"""

import customtkinter as ctk
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ui.screens.login import LoginScreen
from logic.auth import AuthManager
from utils.session import SessionManager

# Carregar variáveis de ambiente
load_dotenv()


class App(ctk.CTk):
    """Main application class"""

    def __init__(self):
        super().__init__()

        # Configurar janela
        self.title(os.getenv("APP_NAME", "Agora Media Production"))
        self.geometry("1200x800")

        # Inicializar gerenciadores
        self.setup_database()
        self.session_manager = SessionManager()

        # Container principal
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # Verificar sessão existente
        self.check_existing_session()

    def setup_database(self):
        """Configure database connection"""
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            print("WARNING: DATABASE_URL not set in .env file")
            # Use SQLite as fallback for development
            database_url = "sqlite:///./agora_media.db"

        try:
            self.engine = create_engine(database_url)
            Session = sessionmaker(bind=self.engine)
            self.db_session = Session()
            self.auth_manager = AuthManager(self.db_session)
        except Exception as e:
            print(f"Database connection error: {e}")
            # Continue anyway for UI testing
            self.db_session = None
            self.auth_manager = None

    def check_existing_session(self):
        """Check if user has an existing valid session"""
        session_data = self.session_manager.load_session()

        if session_data:
            token, user_data = session_data

            # Verify token is still valid
            if self.auth_manager:
                try:
                    valid, updated_user_data = self.auth_manager.verify_token(token)

                    if valid:
                        # Session is valid, show main app
                        self.show_main_app(updated_user_data or user_data)
                        return
                except Exception as e:
                    print(f"Token verification error: {e}")
                    # Clear invalid session
                    self.session_manager.clear_session()

        # No valid session, show login screen
        self.show_login_screen()

    def show_login_screen(self):
        """Display login screen"""
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Create and show login screen
        login_screen = LoginScreen(
            self.main_container,
            on_login_success=self.on_login_success
        )
        login_screen.pack(fill="both", expand=True)

        # Set login callback
        login_screen.set_login_callback(self.handle_login)

    def handle_login(self, email: str, password: str):
        """
        Handle login attempt

        Args:
            email: User's email
            password: User's password

        Returns:
            Tuple of (success, token, user_data)
        """
        if not self.auth_manager:
            print("Auth manager not initialized")
            return False, None, None

        success, token, user_data = self.auth_manager.login(email, password)
        return success, token, user_data

    def on_login_success(self, token: str, user_data: dict):
        """
        Called when login is successful

        Args:
            token: JWT authentication token
            user_data: User information dictionary
        """
        # Save session
        self.session_manager.save_session(token, user_data)

        # Show main application
        self.show_main_app(user_data)

    def show_main_app(self, user_data: dict):
        """
        Display main application interface

        Args:
            user_data: User information dictionary
        """
        # Import here to avoid circular imports
        from ui.main_window import MainWindow

        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Create main window with sidebar and content area
        main_window = MainWindow(
            self.main_container,
            db_session=self.db_session,
            user_data=user_data,
            on_logout=self.logout
        )
        main_window.pack(fill="both", expand=True)

    def logout(self):
        """Handle user logout"""
        # Clear session
        self.session_manager.clear_session()

        # Show login screen
        self.show_login_screen()

    def on_closing(self):
        """Handle application closing"""
        # Close database connection
        if self.db_session:
            self.db_session.close()

        # Destroy window
        self.destroy()


def main():
    """Main entry point"""

    # Configurar tema do CustomTkinter
    ctk.set_appearance_mode("dark")  # "dark" ou "light"
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

    # Criar e executar aplicação
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()

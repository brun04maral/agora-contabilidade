# -*- coding: utf-8 -*-
"""
Login screen UI using CustomTkinter
"""
import customtkinter as ctk
from typing import Callable, Optional
from assets.resources import get_logo


class LoginScreen(ctk.CTkFrame):
    """
    Login screen for user authentication
    """

    def __init__(self, parent, on_login_success: Callable, **kwargs):
        """
        Initialize login screen

        Args:
            parent: Parent widget
            on_login_success: Callback function to call on successful login
                              Signature: on_login_success(token: str, user_data: dict)
        """
        super().__init__(parent, **kwargs)

        self.on_login_success = on_login_success
        self.login_callback: Optional[Callable] = None

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main container
        self.create_widgets()

    def create_widgets(self):
        """Create and layout all widgets"""

        # Main login container
        login_container = ctk.CTkFrame(self, fg_color="transparent")
        login_container.grid(row=0, column=0, sticky="nsew")
        login_container.grid_columnconfigure(0, weight=1)

        # Logo/Title (SVG escalável)
        logo_image = get_logo("logo.svg", size=(313, 80))
        if logo_image:
            logo_ctk = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(313, 80)
            )
            title_label = ctk.CTkLabel(
                login_container,
                image=logo_ctk,
                text=""
            )
            title_label.grid(row=0, column=0, pady=(100, 20), padx=20)
        else:
            # Fallback se logo não carregar
            title_label = ctk.CTkLabel(
                login_container,
                text="AGORA\nMedia Production",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            title_label.grid(row=0, column=0, pady=(100, 10), padx=20)

        subtitle_label = ctk.CTkLabel(
            login_container,
            text="Sistema de Gestão Contabilística",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 40), padx=20)

        # Login form frame
        form_frame = ctk.CTkFrame(login_container)
        form_frame.grid(row=2, column=0, pady=20, padx=50, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)

        # Email label and entry
        email_label = ctk.CTkLabel(
            form_frame,
            text="Email:",
            font=ctk.CTkFont(size=12)
        )
        email_label.grid(row=0, column=0, pady=(20, 5), padx=20, sticky="w")

        self.email_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="seu.email@exemplo.com",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.email_entry.grid(row=1, column=0, pady=(0, 15), padx=20, sticky="ew")

        # Password label and entry
        password_label = ctk.CTkLabel(
            form_frame,
            text="Senha:",
            font=ctk.CTkFont(size=12)
        )
        password_label.grid(row=2, column=0, pady=(0, 5), padx=20, sticky="w")

        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Digite sua senha",
            show="*",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.password_entry.grid(row=3, column=0, pady=(0, 20), padx=20, sticky="ew")

        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="red"
        )
        self.error_label.grid(row=4, column=0, pady=(0, 10), padx=20)
        self.error_label.grid_remove()  # Hide initially

        # Login button
        self.login_button = ctk.CTkButton(
            form_frame,
            text="Entrar",
            command=self._on_login_clicked,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.login_button.grid(row=5, column=0, pady=(10, 30), padx=20, sticky="ew")

        # Bind Enter key to login
        self.email_entry.bind("<Return>", lambda e: self._on_login_clicked())
        self.password_entry.bind("<Return>", lambda e: self._on_login_clicked())

        # Footer
        footer_label = ctk.CTkLabel(
            login_container,
            text="© 2025 Agora Media Production",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        footer_label.grid(row=3, column=0, pady=(40, 20), padx=20)

    def set_login_callback(self, callback: Callable):
        """
        Set the callback function for login attempts

        Args:
            callback: Function to call when login is attempted
                      Signature: callback(email: str, password: str) -> (success: bool, token: str, user_data: dict)
        """
        self.login_callback = callback

    def _on_login_clicked(self):
        """Handle login button click"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        # Validate inputs
        if not email:
            self.show_error("Por favor, insira seu email")
            return

        if not password:
            self.show_error("Por favor, insira sua senha")
            return

        # Clear any previous errors
        self.hide_error()

        # Disable login button during authentication
        self.login_button.configure(state="disabled", text="Autenticando...")

        # Call login callback if set
        if self.login_callback:
            success, token, user_data = self.login_callback(email, password)

            if success and token and user_data:
                # Clear password field
                self.password_entry.delete(0, 'end')
                # Call success callback
                self.on_login_success(token, user_data)
            else:
                self.show_error("Email ou senha incorretos")
                self.login_button.configure(state="normal", text="Entrar")
        else:
            self.show_error("Sistema de autenticação não configurado")
            self.login_button.configure(state="normal", text="Entrar")

    def show_error(self, message: str):
        """
        Display error message

        Args:
            message: Error message to display
        """
        self.error_label.configure(text=message)
        self.error_label.grid()

    def hide_error(self):
        """Hide error message"""
        self.error_label.grid_remove()

    def reset_form(self):
        """Reset form to initial state"""
        self.email_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.hide_error()
        self.login_button.configure(state="normal", text="Entrar")

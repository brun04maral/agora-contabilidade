# -*- coding: utf-8 -*-
"""
Main window - Janela principal da aplicação
"""
import customtkinter as ctk
from sqlalchemy.orm import Session

from ui.components.sidebar import Sidebar
from ui.screens.saldos import SaldosScreen


class MainWindow(ctk.CTkFrame):
    """
    Janela principal com sidebar e área de conteúdo
    """

    def __init__(self, parent, db_session: Session, user_data: dict, on_logout: callable, **kwargs):
        """
        Initialize main window

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
            user_data: User information dict
            on_logout: Callback for logout
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.user_data = user_data
        self.on_logout = on_logout

        # Initialize current screen (needed before create_widgets)
        self.current_screen = None

        # Configure
        self.configure(fg_color="transparent")

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=1)  # Content (expandable)

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        """Create main window widgets"""

        # Content area (create BEFORE sidebar, as sidebar needs it during init)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Sidebar (created after content_frame so it can use it)
        self.sidebar = Sidebar(self, on_menu_select=self.on_menu_select, width=260)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

    def on_menu_select(self, menu_id: str):
        """
        Handle menu selection

        Args:
            menu_id: Selected menu identifier
        """

        # Clear current screen
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Show selected screen
        if menu_id == "dashboard":
            self.show_dashboard()
        elif menu_id == "saldos":
            self.show_saldos()
        elif menu_id == "projetos":
            self.show_projetos()
        elif menu_id == "despesas":
            self.show_despesas()
        elif menu_id == "boletins":
            self.show_boletins()
        elif menu_id == "clientes":
            self.show_clientes()
        elif menu_id == "fornecedores":
            self.show_fornecedores()
        elif menu_id == "settings":
            self.show_settings()
        elif menu_id == "logout":
            self.handle_logout()

    def show_dashboard(self):
        """Show dashboard screen"""
        from ui.screens.dashboard_melhorado import DashboardMelhorado
        screen = DashboardMelhorado(self.content_frame, self.db_session)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_saldos(self):
        """Show saldos pessoais screen"""
        screen = SaldosScreen(self.content_frame, self.db_session)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_projetos(self):
        """Show projetos screen"""
        from ui.screens.projetos import ProjetosScreen
        screen = ProjetosScreen(self.content_frame, self.db_session)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_despesas(self):
        """Show despesas screen"""
        from ui.screens.despesas import DespesasScreen
        screen = DespesasScreen(self.content_frame, self.db_session)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_boletins(self):
        """Show boletins screen"""
        from ui.screens.boletins import BoletinsScreen
        screen = BoletinsScreen(self.content_frame, self.db_session)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_clientes(self):
        """Show clientes screen"""
        from ui.screens.clientes import ClientesScreen
        screen = ClientesScreen(self.content_frame, self.db_session)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_fornecedores(self):
        """Show fornecedores screen"""
        from ui.screens.fornecedores import FornecedoresScreen
        screen = FornecedoresScreen(self.content_frame, self.db_session)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_settings(self):
        """Show settings screen"""
        screen = ctk.CTkFrame(self.content_frame)
        screen.grid(row=0, column=0, sticky="nsew")

        # Header
        header_frame = ctk.CTkFrame(screen, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ Definições",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(anchor="w")

        # User info
        info_frame = ctk.CTkFrame(screen)
        info_frame.pack(fill="x", padx=30, pady=20)

        user_label = ctk.CTkLabel(
            info_frame,
            text=f"Utilizador: {self.user_data.get('name', 'N/A')}",
            font=ctk.CTkFont(size=16)
        )
        user_label.pack(anchor="w", padx=20, pady=(20, 5))

        email_label = ctk.CTkLabel(
            info_frame,
            text=f"Email: {self.user_data.get('email', 'N/A')}",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        email_label.pack(anchor="w", padx=20, pady=(0, 5))

        role_label = ctk.CTkLabel(
            info_frame,
            text=f"Função: {self.user_data.get('role', 'N/A')}",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        role_label.pack(anchor="w", padx=20, pady=(0, 20))

        self.current_screen = screen

    def handle_logout(self):
        """Handle logout"""
        if self.on_logout:
            self.on_logout()

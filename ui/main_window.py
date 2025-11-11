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
        elif menu_id == "orcamentos":
            self.show_orcamentos()
        elif menu_id == "despesas":
            self.show_despesas()
        elif menu_id == "boletins":
            self.show_boletins()
        elif menu_id == "relatorios":
            self.show_relatorios()
        elif menu_id == "clientes":
            self.show_clientes()
        elif menu_id == "fornecedores":
            self.show_fornecedores()
        elif menu_id == "equipamento":
            self.show_equipamento()
        elif menu_id == "info":
            self.show_info()
        elif menu_id == "logout":
            self.handle_logout()

    def show_dashboard(self):
        """Show dashboard screen"""
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("dashboard")

        from ui.screens.dashboard import DashboardScreen
        screen = DashboardScreen(self.content_frame, self.db_session, self)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_saldos(self):
        """Show saldos pessoais screen"""
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("saldos")

        screen = SaldosScreen(self.content_frame, self.db_session, main_window=self)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_projetos(self, filtro_estado=None, filtro_cliente_id=None, filtro_tipo=None):
        """
        Show projetos screen

        Args:
            filtro_estado: Optional estado filter ("Todos", "Recebido", "Faturado", "Não Faturado")
            filtro_cliente_id: Optional cliente ID to filter by
            filtro_tipo: Optional tipo filter ("Pessoal BA", "Pessoal RR", "Empresa")
        """
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("projetos")

        from ui.screens.projetos import ProjetosScreen
        screen = ProjetosScreen(self.content_frame, self.db_session, filtro_estado=filtro_estado, filtro_cliente_id=filtro_cliente_id, filtro_tipo=filtro_tipo)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_despesas(self, filtro_estado=None):
        """
        Show despesas screen

        Args:
            filtro_estado: Optional estado filter ("Todos", "Ativo", "Vencido", "Pago")
        """
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("despesas")

        from ui.screens.despesas import DespesasScreen
        screen = DespesasScreen(self.content_frame, self.db_session, filtro_estado=filtro_estado)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_boletins(self, filtro_estado=None):
        """
        Show boletins screen

        Args:
            filtro_estado: Optional estado filter ("Todos", "Pendente", "Pago")
        """
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("boletins")

        from ui.screens.boletins import BoletinsScreen
        screen = BoletinsScreen(self.content_frame, self.db_session, filtro_estado=filtro_estado)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_relatorios(self, projeto_ids=None, despesa_ids=None, boletim_ids=None):
        """
        Show relatorios screen

        Args:
            projeto_ids: Optional list of project IDs to pre-filter report
            despesa_ids: Optional list of despesa IDs to pre-filter report
            boletim_ids: Optional list of boletim IDs to pre-filter report
        """
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("relatorios")

        from ui.screens.relatorios import RelatoriosScreen
        screen = RelatoriosScreen(self.content_frame, self.db_session, projeto_ids=projeto_ids, despesa_ids=despesa_ids, boletim_ids=boletim_ids)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_clientes(self):
        """Show clientes screen"""
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("clientes")

        from ui.screens.clientes import ClientesScreen
        screen = ClientesScreen(self.content_frame, self.db_session, self)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_fornecedores(self):
        """Show fornecedores screen"""
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("fornecedores")

        from ui.screens.fornecedores import FornecedoresScreen
        screen = FornecedoresScreen(self.content_frame, self.db_session)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_equipamento(self):
        """Show equipamento screen"""
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("equipamento")

        from ui.screens.equipamento import EquipamentoScreen
        screen = EquipamentoScreen(self.content_frame, self.db_session)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_orcamentos(self, filtro_tipo=None, filtro_status=None, filtro_cliente_id=None):
        """
        Show orcamentos screen

        Args:
            filtro_tipo: Optional tipo filter ("frontend", "backend")
            filtro_status: Optional status filter ("rascunho", "enviado", "aprovado", "rejeitado")
            filtro_cliente_id: Optional cliente ID to filter by
        """
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("orcamentos")

        from ui.screens.orcamentos import OrcamentosScreen
        screen = OrcamentosScreen(
            self.content_frame,
            self.db_session,
            filtro_tipo=filtro_tipo,
            filtro_status=filtro_status,
            filtro_cliente_id=filtro_cliente_id
        )
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def show_info(self):
        """Show info screen"""
        # Clear current screen if navigating programmatically
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

        # Update sidebar selection (visual only, no callback)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_selection("info")

        from ui.screens.info import InfoScreen
        screen = InfoScreen(self.content_frame)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen

    def handle_logout(self):
        """Handle logout"""
        if self.on_logout:
            self.on_logout()

# -*- coding: utf-8 -*-
"""
Screen de Templates de Boletins Recorrentes
Gestão de templates para geração automática de boletins mensais
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
import tkinter.messagebox as messagebox

from logic.boletim_templates import BoletimTemplatesManager
from database.models.boletim_template import Socio
from ui.components.data_table_v2 import DataTableV2


class TemplatesBoletinsScreen(ctk.CTkFrame):
    """
    Tela de gestão de Templates de Boletins Recorrentes (CRUD completo)
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = BoletimTemplatesManager(db_session)

        self.create_layout()
        self.carregar_templates()

    def create_layout(self):
        """Create screen layout"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        ctk.CTkLabel(
            header_frame,
            text="🔁 Templates de Boletins Recorrentes",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_templates,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=5)

        novo_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Novo Template",
            command=self.abrir_formulario,
            width=160,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#64B5F6", "#1565C0")
        )
        novo_btn.pack(side="left", padx=5)

        # Info text
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(
            info_frame,
            text="💡 Templates para geração automática de boletins mensais. Geram cabeçalho vazio no dia especificado.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(anchor="w")

        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Data table
        columns = [
            {"key": "numero", "label": "Número", "width": 120},
            {"key": "nome", "label": "Nome", "width": 200},
            {"key": "socio", "label": "Sócio", "width": 100},
            {"key": "dia_mes", "label": "Dia do Mês", "width": 120},
            {"key": "ativo", "label": "Ativo", "width": 100},
        ]

        self.table = DataTableV2(
            table_frame,
            columns=columns,
            on_row_double_click=self.editar_template
        )
        self.table.pack(fill="both", expand=True)

    def carregar_templates(self):
        """Load templates into table"""
        templates = self.manager.listar_todos()
        data = [self.template_to_dict(t) for t in templates]
        self.table.set_data(data)

    def template_to_dict(self, template) -> dict:
        """Convert template to dict for table display"""
        return {
            'id': template.id,
            'numero': template.numero,
            'nome': template.nome,
            'socio': template.socio.value,
            'dia_mes': str(template.dia_mes),
            'ativo': "✅ Sim" if template.ativo else "❌ Não",
            '_template': template  # Store original object
        }

    def abrir_formulario(self):
        """Open form dialog for new template"""
        dialog = FormularioTemplateDialog(self, self.db_session)
        dialog.wait_window()
        self.carregar_templates()
        self.table.clear_selection()

    def editar_template(self, row_data):
        """Edit template (double-click handler)"""
        template = row_data.get('_template')
        if not template:
            return

        dialog = FormularioTemplateDialog(self, self.db_session, template=template)
        dialog.wait_window()
        self.carregar_templates()
        self.table.clear_selection()


class FormularioTemplateDialog(ctk.CTkToplevel):
    """
    Dialog para criar/editar templates de boletins
    """

    def __init__(self, parent, db_session: Session, template=None):
        super().__init__(parent)

        self.db_session = db_session
        self.manager = BoletimTemplatesManager(db_session)
        self.template = template  # None = criar novo, objeto = editar

        # Window config
        self.title("Editar Template" if template else "Novo Template")
        self.geometry("550x500")
        self.resizable(False, False)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_layout()
        if template:
            self.preencher_dados(template)

    def create_layout(self):
        """Create dialog layout"""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=(30, 20))

        ctk.CTkLabel(
            title_frame,
            text="✏️ Editar Template" if self.template else "➕ Novo Template",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w")

        # Form frame
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Número
        ctk.CTkLabel(form_frame, text="Número:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.numero_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        self.numero_entry.pack(fill="x", pady=(0, 10))
        if self.template:
            self.numero_entry.configure(state="disabled")  # Não pode mudar o número ao editar

        # Nome
        ctk.CTkLabel(form_frame, text="Nome:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.nome_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        self.nome_entry.pack(fill="x", pady=(0, 10))

        # Sócio
        ctk.CTkLabel(form_frame, text="Sócio:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.socio_dropdown = ctk.CTkOptionMenu(
            form_frame,
            values=[socio.value for socio in Socio],
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.socio_dropdown.pack(fill="x", pady=(0, 10))

        # Dia do Mês
        ctk.CTkLabel(form_frame, text="Dia do Mês (1-31):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.dia_mes_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        self.dia_mes_entry.pack(fill="x", pady=(0, 10))

        # Ativo
        ctk.CTkLabel(form_frame, text="Ativo:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.ativo_switch = ctk.CTkSwitch(
            form_frame,
            text="Gerar boletins automaticamente",
            font=ctk.CTkFont(size=13)
        )
        self.ativo_switch.pack(anchor="w", pady=(0, 10))
        self.ativo_switch.select()  # Default: ativo

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 30))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=self.destroy,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Gravar",
            command=self.gravar,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        save_btn.pack(side="left")

        # Delete button (only when editing)
        if self.template:
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️ Apagar",
                command=self.apagar,
                width=140,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color=("#F44336", "#C62828"),
                hover_color=("#E57373", "#B71C1C")
            )
            delete_btn.pack(side="right")

    def preencher_dados(self, template):
        """Fill form with existing data"""
        self.numero_entry.insert(0, template.numero)
        self.nome_entry.insert(0, template.nome)
        self.socio_dropdown.set(template.socio.value)
        self.dia_mes_entry.insert(0, str(template.dia_mes))
        if template.ativo:
            self.ativo_switch.select()
        else:
            self.ativo_switch.deselect()

    def gravar(self):
        """Save template"""
        try:
            # Get values
            numero = self.numero_entry.get().strip()
            nome = self.nome_entry.get().strip()
            socio_str = self.socio_dropdown.get()
            dia_mes_str = self.dia_mes_entry.get().strip()
            ativo = self.ativo_switch.get() == 1

            # Validations
            if not numero:
                messagebox.showerror("Erro", "Número é obrigatório")
                return

            if not nome:
                messagebox.showerror("Erro", "Nome é obrigatório")
                return

            if not dia_mes_str:
                messagebox.showerror("Erro", "Dia do mês é obrigatório")
                return

            # Convert
            try:
                socio = Socio(socio_str)
            except ValueError:
                messagebox.showerror("Erro", f"Sócio inválido: {socio_str}")
                return

            try:
                dia_mes = int(dia_mes_str)
            except ValueError:
                messagebox.showerror("Erro", "Dia do mês deve ser um número")
                return

            if dia_mes < 1 or dia_mes > 31:
                messagebox.showerror("Erro", "Dia do mês deve estar entre 1 e 31")
                return

            # Save
            if self.template:
                # Update
                sucesso, _, erro = self.manager.atualizar(
                    numero=numero,
                    nome=nome,
                    socio=socio,
                    dia_mes=dia_mes,
                    ativo=ativo
                )
            else:
                # Create
                sucesso, _, erro = self.manager.criar(
                    numero=numero,
                    nome=nome,
                    socio=socio,
                    dia_mes=dia_mes,
                    ativo=ativo
                )

            if sucesso:
                self.destroy()
            else:
                messagebox.showerror("Erro", erro or "Erro ao gravar")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def apagar(self):
        """Delete template"""
        if not self.template:
            return

        resposta = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja apagar o template {self.template.numero}?\n\n"
            "ATENÇÃO: Boletins já gerados não serão afetados."
        )

        if resposta:
            sucesso, erro = self.manager.eliminar(self.template.numero)
            if sucesso:
                self.destroy()
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar")

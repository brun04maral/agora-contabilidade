# -*- coding: utf-8 -*-
"""
Screen de Valores de Referência Anuais
Configuração de valores de referência para boletins por ano
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from decimal import Decimal
import tkinter.messagebox as messagebox

from logic.valores_referencia import ValoresReferenciaManager
from ui.components.data_table_v2 import DataTableV2
from utils.base_dialogs import BaseDialogMedium


class ValoresReferenciaScreen(ctk.CTkFrame):
    """
    Tela de gestão de Valores de Referência Anuais (CRUD completo)
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = ValoresReferenciaManager(db_session)

        self.create_layout()
        self.carregar_valores()

    def create_layout(self):
        """Create screen layout"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        ctk.CTkLabel(
            header_frame,
            text="⚙️ Valores de Referência Anuais",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_valores,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=5)

        nova_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Novo Ano",
            command=self.abrir_formulario,
            width=140,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#64B5F6", "#1565C0")
        )
        nova_btn.pack(side="left", padx=5)

        # Info text
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(
            info_frame,
            text="💡 Valores de referência usados nos cálculos de ajudas de custo e quilómetros dos boletins.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(anchor="w")

        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Data table
        columns = [
            {"key": "ano", "label": "Ano", "width": 100},
            {"key": "val_dia_nacional", "label": "Dia Nacional", "width": 140},
            {"key": "val_dia_estrangeiro", "label": "Dia Estrangeiro", "width": 150},
            {"key": "val_km", "label": "€/Km", "width": 100},
        ]

        self.table = DataTableV2(
            table_frame,
            columns=columns,
            on_row_double_click=self.editar_valor
        )
        self.table.pack(fill="both", expand=True)

    def carregar_valores(self):
        """Load valores into table"""
        valores = self.manager.listar_todos()
        data = [self.valor_to_dict(v) for v in valores]
        self.table.set_data(data)

    def valor_to_dict(self, valor) -> dict:
        """Convert valor to dict for table display"""
        return {
            'id': valor.id,
            'ano': valor.ano,
            'val_dia_nacional': f"€{float(valor.val_dia_nacional):.2f}",
            'val_dia_estrangeiro': f"€{float(valor.val_dia_estrangeiro):.2f}",
            'val_km': f"€{float(valor.val_km):.2f}",
            '_valor': valor  # Store original object
        }

    def abrir_formulario(self):
        """Open form dialog for new valor"""
        dialog = FormularioValorDialog(self, self.db_session)
        dialog.wait_window()
        self.carregar_valores()
        self.table.clear_selection()

    def editar_valor(self, row_data):
        """Edit valor (double-click handler)"""
        valor = row_data.get('_valor')
        if not valor:
            return

        dialog = FormularioValorDialog(self, self.db_session, valor=valor)
        dialog.wait_window()
        self.carregar_valores()
        self.table.clear_selection()


class FormularioValorDialog(BaseDialogMedium):
    """
    Dialog para criar/editar valores de referência
    """

    def __init__(self, parent, db_session: Session, valor=None):
        self.db_session = db_session
        self.manager = ValoresReferenciaManager(db_session)
        self.valor = valor  # None = criar novo, objeto = editar

        title = "Editar Valores" if valor else "Novo Ano"
        super().__init__(parent, title=title)

        self.create_layout()
        if valor:
            self.preencher_dados(valor)

    def create_layout(self):
        """Create dialog layout"""
        # Title
        ctk.CTkLabel(
            self.main_frame,
            text="✏️ Editar Valores" if self.valor else "➕ Novo Ano",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(0, 20))

        # Form frame
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Ano
        ctk.CTkLabel(form_frame, text="Ano:", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.ano_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        self.ano_entry.pack(fill="x", pady=(0, 10))
        if self.valor:
            self.ano_entry.configure(state="disabled")  # Não pode mudar o ano ao editar

        # Val Dia Nacional
        ctk.CTkLabel(form_frame, text="Valor Dia Nacional (€):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.val_nacional_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        self.val_nacional_entry.pack(fill="x", pady=(0, 10))

        # Val Dia Estrangeiro
        ctk.CTkLabel(form_frame, text="Valor Dia Estrangeiro (€):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.val_estrangeiro_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        self.val_estrangeiro_entry.pack(fill="x", pady=(0, 10))

        # Val Km
        ctk.CTkLabel(form_frame, text="Valor por Km (€):", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.val_km_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=13))
        self.val_km_entry.pack(fill="x", pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

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
        if self.valor:
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

    def preencher_dados(self, valor):
        """Fill form with existing data"""
        self.ano_entry.insert(0, str(valor.ano))
        self.val_nacional_entry.insert(0, str(float(valor.val_dia_nacional)))
        self.val_estrangeiro_entry.insert(0, str(float(valor.val_dia_estrangeiro)))
        self.val_km_entry.insert(0, str(float(valor.val_km)))

    def gravar(self):
        """Save values"""
        try:
            # Get values
            ano_str = self.ano_entry.get().strip()
            val_nacional_str = self.val_nacional_entry.get().strip()
            val_estrangeiro_str = self.val_estrangeiro_entry.get().strip()
            val_km_str = self.val_km_entry.get().strip()

            # Validations
            if not ano_str:
                messagebox.showerror("Erro", "Ano é obrigatório")
                return

            if not val_nacional_str or not val_estrangeiro_str or not val_km_str:
                messagebox.showerror("Erro", "Todos os valores são obrigatórios")
                return

            # Convert
            ano = int(ano_str)
            val_nacional = Decimal(val_nacional_str)
            val_estrangeiro = Decimal(val_estrangeiro_str)
            val_km = Decimal(val_km_str)

            # Save
            if self.valor:
                # Update
                sucesso, _, erro = self.manager.atualizar(
                    ano=ano,
                    val_dia_nacional=val_nacional,
                    val_dia_estrangeiro=val_estrangeiro,
                    val_km=val_km
                )
            else:
                # Create
                sucesso, _, erro = self.manager.criar(
                    ano=ano,
                    val_dia_nacional=val_nacional,
                    val_dia_estrangeiro=val_estrangeiro,
                    val_km=val_km
                )

            if sucesso:
                self.destroy()
            else:
                messagebox.showerror("Erro", erro or "Erro ao gravar")

        except ValueError as e:
            messagebox.showerror("Erro", f"Valores inválidos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def apagar(self):
        """Delete valor"""
        if not self.valor:
            return

        resposta = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja apagar os valores de {self.valor.ano}?\n\n"
            "ATENÇÃO: Boletins já criados com estes valores não serão afetados."
        )

        if resposta:
            sucesso, erro = self.manager.eliminar(self.valor.ano)
            if sucesso:
                self.destroy()
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar")

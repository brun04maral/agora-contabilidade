# -*- coding: utf-8 -*-
"""
Tela de gestão de Boletins
"""
import customtkinter as ctk
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
import tkinter.messagebox as messagebox

from logic.boletins import BoletinsManager
from database.models import Socio, EstadoBoletim
from ui.components.data_table_v2 import DataTableV2
from assets.resources import get_icon, BOLETINS


class BoletinsScreen(ctk.CTkFrame):
    """
    Tela de gestão de Boletins (listar + emitir + marcar pago)
    """

    def __init__(self, parent, db_session: Session, filtro_estado=None, filtro_socio=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = BoletinsManager(db_session)
        self.filtro_inicial_estado = filtro_estado
        self.filtro_inicial_socio = filtro_socio

        self.configure(fg_color="transparent")
        self.create_widgets()

        # Apply initial filter if provided
        if self.filtro_inicial_estado or self.filtro_inicial_socio:
            if self.filtro_inicial_estado:
                self.estado_filter.set(self.filtro_inicial_estado)
            if self.filtro_inicial_socio:
                self.socio_filter.set(self.filtro_inicial_socio)
            self.aplicar_filtros()
        else:
            self.carregar_boletins()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(BOLETINS, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Boletins",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="📄 Boletins",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_boletins,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=5)

        novo_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Novo Boletim",
            command=self.abrir_formulario,
            width=150,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        novo_btn.pack(side="left", padx=5)

        # Config button (small, for values)
        config_btn = ctk.CTkButton(
            btn_frame,
            text="⚙️",
            command=self.abrir_valores_referencia,
            width=35,
            height=35,
            font=ctk.CTkFont(size=16),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        config_btn.pack(side="left", padx=(0, 5))

        # Filters
        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Sócio filter
        ctk.CTkLabel(
            filters_frame,
            text="Sócio:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.socio_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "BA", "RR"],
            command=self.aplicar_filtros,
            width=150
        )
        self.socio_filter.pack(side="left", padx=(0, 20))

        # Estado filter
        ctk.CTkLabel(
            filters_frame,
            text="Estado:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.estado_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "Pendente", "Pago"],
            command=self.aplicar_filtros,
            width=120
        )
        self.estado_filter.pack(side="left")

        # Selection actions bar (created but NOT packed - will be shown on selection)
        self.selection_frame = ctk.CTkFrame(self, fg_color="transparent")

        # Clear selection button
        self.cancel_btn = ctk.CTkButton(
            self.selection_frame,
            text="🗑️ Limpar Seleção",
            command=self.cancelar_selecao,
            width=150, height=35
        )

        # Selection count label
        self.count_label = ctk.CTkLabel(
            self.selection_frame,
            text="0 selecionados",
            font=ctk.CTkFont(size=13)
        )

        # Mark as paid button
        self.marcar_pago_btn = ctk.CTkButton(
            self.selection_frame,
            text="✅ Marcar como Pago",
            command=self.marcar_como_pago_batch,
            width=180, height=35,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )

        # Report button
        self.report_btn = ctk.CTkButton(
            self.selection_frame,
            text="📊 Criar Relatório",
            command=self.criar_relatorio,
            width=160, height=35
        )

        # Total label
        self.total_label = ctk.CTkLabel(
            self.selection_frame,
            text="Total: €0,00",
            font=ctk.CTkFont(size=14, weight="bold")
        )

        # Table
        columns = [
            {'key': 'numero', 'label': 'ID', 'width': 80, 'sortable': True},
            {'key': 'socio', 'label': 'Sócio', 'width': 120, 'sortable': True},
            {'key': 'data_emissao', 'label': 'Data Emissão', 'width': 120, 'sortable': True},
            {'key': 'linhas', 'label': 'Linhas', 'width': 80, 'sortable': True},
            {'key': 'valor_fmt', 'label': 'Valor', 'width': 110, 'sortable': True},
            {'key': 'descricao', 'label': 'Descrição', 'width': 220, 'sortable': False},
            {'key': 'estado', 'label': 'Estado', 'width': 100, 'sortable': True},
            {'key': 'data_pagamento', 'label': 'Data Pagamento', 'width': 130, 'sortable': True},
        ]

        self.table = DataTableV2(
            self,
            columns=columns,
            on_row_double_click=self.editar_boletim,
            on_selection_change=self.on_selection_change,
            height=400
        )
        self.table.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    def carregar_boletins(self):
        """Load and display boletins"""
        boletins = self.manager.listar_todos()
        data = [self.boletim_to_dict(b) for b in boletins]
        self.table.set_data(data)

    def boletim_to_dict(self, boletim) -> dict:
        """Convert boletim to dict for table"""
        # Determine color based on estado
        color = self.get_estado_color(boletim.estado)

        # Count linhas (deslocações)
        num_linhas = len(boletim.linhas) if hasattr(boletim, 'linhas') and boletim.linhas else 0

        return {
            'id': boletim.id,
            'numero': boletim.numero,
            'socio': "BA" if boletim.socio == Socio.BRUNO else "RR",
            'data_emissao': boletim.data_emissao.strftime("%Y-%m-%d") if boletim.data_emissao else '-',
            'linhas': str(num_linhas),
            'valor': float(boletim.valor),
            'valor_fmt': f"€{float(boletim.valor):,.2f}",
            'descricao': boletim.descricao or '-',
            'estado': "Pendente" if boletim.estado == EstadoBoletim.PENDENTE else "Pago",
            'data_pagamento': boletim.data_pagamento.strftime("%Y-%m-%d") if boletim.data_pagamento else '-',
            '_bg_color': color,
            '_boletim': boletim
        }

    def get_estado_color(self, estado: EstadoBoletim) -> tuple:
        """Get color for estado (returns tuple: light, dark mode) - Opção 3 Agora Inspired"""
        color_map = {
            EstadoBoletim.PENDENTE: ("#FFE5D0", "#8B4513"),  # Laranja pastel - atenção
            EstadoBoletim.PAGO: ("#E8F5E0", "#4A7028")        # Verde pastel - positivo
        }
        return color_map.get(estado, ("#E0E0E0", "#4A4A4A"))

    def aplicar_filtros(self, *args):
        """Apply filters"""
        socio = self.socio_filter.get()
        estado = self.estado_filter.get()

        boletins = self.manager.listar_todos()

        # Filter by socio
        if socio != "Todos":
            socio_enum = Socio.BRUNO if socio == "BA" else Socio.RAFAEL
            boletins = [b for b in boletins if b.socio == socio_enum]

        # Filter by estado
        if estado != "Todos":
            estado_enum = EstadoBoletim.PENDENTE if estado == "Pendente" else EstadoBoletim.PAGO
            boletins = [b for b in boletins if b.estado == estado_enum]

        data = [self.boletim_to_dict(b) for b in boletins]
        self.table.set_data(data)

        # Clear selection when filters change
        self.table.clear_selection()

    def after_save_callback(self):
        """Callback after saving - reload data and clear selection"""
        self.carregar_boletins()
        self.table.clear_selection()

    def abrir_formulario(self, boletim=None):
        """Open form editor (new BoletimFormScreen)"""
        from ui.screens.boletim_form import BoletimFormScreen
        dialog = BoletimFormScreen(self, self.db_session, boletim=boletim, callback=self.after_save_callback)

    def editar_boletim(self, data: dict):
        """Edit boletim (triggered by double-click)"""
        boletim = data.get('_boletim')
        if boletim:
            self.abrir_formulario(boletim)

    def on_selection_change(self, selected_data: list):
        """Handle selection change in table"""
        num_selected = len(selected_data)

        if num_selected > 0:
            # Show selection frame
            self.selection_frame.pack(fill="x", padx=30, pady=(0, 10))

            # Show selection bar
            self.cancel_btn.pack(side="left", padx=5)

            # Show count
            count_text = f"{num_selected} selecionado" if num_selected == 1 else f"{num_selected} selecionados"
            self.count_label.configure(text=count_text)
            self.count_label.pack(side="left", padx=15)

            # Show "Marcar como Pago" only if there are unpaid boletins
            has_unpaid = any(
                item.get('_boletim') and item.get('_boletim').estado != EstadoBoletim.PAGO
                for item in selected_data
            )
            if has_unpaid:
                self.marcar_pago_btn.pack(side="left", padx=5)

            self.report_btn.pack(side="left", padx=5)

            # Calculate and show total
            total = sum(item.get('valor', 0) for item in selected_data)
            self.total_label.configure(text=f"Total: €{total:,.2f}")
            self.total_label.pack(side="left", padx=20)
        else:
            # Hide entire selection frame when nothing is selected
            self.selection_frame.pack_forget()

    def cancelar_selecao(self):
        """Cancel selection"""
        self.table.clear_selection()

    def marcar_como_pago_batch(self):
        """Mark selected boletins as paid"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) == 0:
            return

        # Filter only unpaid boletins
        unpaid_boletins = [
            item.get('_boletim') for item in selected_data
            if item.get('_boletim') and item.get('_boletim').estado != EstadoBoletim.PAGO
        ]

        if len(unpaid_boletins) == 0:
            messagebox.showinfo("Info", "Todos os boletins selecionados já estão pagos.")
            return

        # Confirm action
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Marcar {len(unpaid_boletins)} boletim(ns) como pago(s)?\n\n"
            f"Data de pagamento será definida como hoje ({date.today().strftime('%Y-%m-%d')})."
        )

        if resposta:
            hoje = date.today()
            erros = []

            for boletim in unpaid_boletins:
                sucesso, erro = self.manager.marcar_como_pago(boletim.id)
                if not sucesso:
                    erros.append(f"{boletim.numero}: {erro}")

            if len(erros) == 0:
                self.carregar_boletins()
                self.table.clear_selection()
            else:
                messagebox.showerror("Erro", f"Erros ao marcar boletins:\n" + "\n".join(erros))
                self.carregar_boletins()

    def criar_relatorio(self):
        """Create report for selected boletins and navigate to Relatorios tab"""
        selected_data = self.table.get_selected_data()
        if len(selected_data) > 0:
            # Extract boletim IDs from selected data
            boletim_ids = [item.get('id') for item in selected_data if item.get('id')]

            # Navigate to Relatorios tab with selected boletim IDs
            main_window = self.master.master
            if hasattr(main_window, 'show_relatorios'):
                main_window.show_relatorios(boletim_ids=boletim_ids)
            else:
                messagebox.showerror("Erro", "Não foi possível navegar para a aba de Relatórios")

    def abrir_valores_referencia(self):
        """Open valores de referência screen (config)"""
        from ui.screens.valores_referencia import ValoresReferenciaScreen

        # Open in modal window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Valores de Referência por Ano")
        dialog.geometry("900x600")

        # Center window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Make modal
        dialog.transient(self)
        dialog.grab_set()

        # Create screen inside dialog
        screen = ValoresReferenciaScreen(dialog, self.db_session)
        screen.pack(fill="both", expand=True)



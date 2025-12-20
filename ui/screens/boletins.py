# -*- coding: utf-8 -*-
"""
Tela de gestão de Boletins
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import date
import tkinter.messagebox as messagebox

from logic.boletins import BoletinsManager
from database.models import Socio, EstadoBoletim
from ui.components.base_screen import BaseScreen
from assets.resources import get_icon, BOLETINS


class BoletinsScreen(BaseScreen):
    """
    Tela de gestão de Boletins (listar + emitir + marcar pago)
    """

    def __init__(self, parent, db_session: Session, filtro_estado=None, filtro_socio=None, **kwargs):
        self.db_session = db_session
        self.manager = BoletinsManager(db_session)
        self.filtro_inicial_estado = filtro_estado
        self.filtro_inicial_socio = filtro_socio

        # Initialize filter widgets (created in toolbar_slot)
        self.socio_filter = None
        self.estado_filter = None

        # Call parent __init__ (this will call abstract methods)
        super().__init__(parent, db_session, **kwargs)

    # ===== ABSTRACT METHODS FROM BaseScreen =====

    def get_screen_title(self) -> str:
        """Return screen title"""
        return "Boletins"

    def get_screen_icon(self):
        """Return screen icon (PIL Image or None)"""
        return get_icon(BOLETINS, size=(28, 28))

    def get_table_columns(self) -> List[Dict[str, Any]]:
        """Return table column definitions"""
        return [
            {'key': 'numero', 'label': 'ID', 'width': 80, 'sortable': True},
            {'key': 'socio', 'label': 'Sócio', 'width': 120, 'sortable': True},
            {'key': 'data_emissao', 'label': 'Data Emissão', 'width': 120, 'sortable': True},
            {'key': 'linhas', 'label': 'Linhas', 'width': 80, 'sortable': True},
            {'key': 'valor_fmt', 'label': 'Valor', 'width': 110, 'sortable': True},
            {'key': 'descricao', 'label': 'Descrição', 'width': 220, 'sortable': False},
            {'key': 'estado', 'label': 'Estado', 'width': 100, 'sortable': True},
            {'key': 'data_pagamento', 'label': 'Data Pagamento', 'width': 130, 'sortable': True},
        ]

    def load_data(self) -> List[Any]:
        """Load boletins from database and return as list of objects"""
        try:
            # Get dropdown filters (widgets podem não existir em __init__)
            socio = "Todos"
            if hasattr(self, 'socio_filter') and self.socio_filter:
                try:
                    socio = self.socio_filter.get()
                except Exception:
                    pass

            estado = "Todos"
            if hasattr(self, 'estado_filter') and self.estado_filter:
                try:
                    estado = self.estado_filter.get()
                except Exception:
                    pass

            # Load all boletins
            boletins = self.manager.listar_todos()

            # Apply socio filter
            if socio != "Todos":
                socio_enum = Socio.BA if socio == "BA" else Socio.RR
                boletins = [b for b in boletins if b.socio == socio_enum]

            # Apply estado filter
            if estado != "Todos":
                estado_enum = EstadoBoletim.PENDENTE if estado == "Pendente" else EstadoBoletim.PAGO
                boletins = [b for b in boletins if b.estado == estado_enum]

            return boletins  # NUNCA None, sempre lista

        except Exception as e:
            print(f"ERROR in load_data(): {e}")
            import traceback
            traceback.print_exc()
            return []  # SEMPRE retornar lista vazia em erro

    def item_to_dict(self, item: Any) -> Dict[str, Any]:
        """Convert boletim object to dict for table"""
        # Count linhas (deslocações)
        num_linhas = len(item.linhas) if hasattr(item, 'linhas') and item.linhas else 0

        return {
            'id': item.id,
            'numero': item.numero,
            'socio': "BA" if item.socio == Socio.BA else "RR",
            'data_emissao': item.data_emissao.strftime("%Y-%m-%d") if item.data_emissao else '-',
            'linhas': str(num_linhas),
            'valor': float(item.valor),
            'valor_fmt': f"€{float(item.valor):,.2f}",
            'descricao': item.descricao or '-',
            'estado': "Pendente" if item.estado == EstadoBoletim.PENDENTE else "Pago",
            'data_pagamento': item.data_pagamento.strftime("%Y-%m-%d") if item.data_pagamento else '-',
            '_bg_color': self.get_estado_color(item.estado),
            '_boletim': item  # CRÍTICO: guardar objeto original
        }

    def get_context_menu_items(self, data: dict) -> List[Dict[str, Any]]:
        """Define ações do context menu e barra de ações"""

        # Para barra de ações (data vazio {} quando BaseScreen chama)
        if not data or '_boletim' not in data:
            return [
                {
                    'label': '✏️ Editar',
                    'command': self._editar_selecionado,
                    'min_selection': 1,
                    'max_selection': 1,
                    'fg_color': ('#2196F3', '#1976D2'),
                    'hover_color': ('#1976D2', '#1565C0'),
                    'width': 100
                },
                {
                    'label': '📋 Duplicar',
                    'command': self._duplicar_selecionado,
                    'min_selection': 1,
                    'max_selection': 1,  # ⚠️ Apenas 1 por vez
                    'fg_color': ('#9C27B0', '#7B1FA2'),
                    'hover_color': ('#7B1FA2', '#6A1B9A'),
                    'width': 110
                },
                {
                    'label': '✅ Marcar Pago',
                    'command': self._pagar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#4CAF50', '#388E3C'),
                    'hover_color': ('#388E3C', '#2E7D32'),
                    'width': 130
                },
                {
                    'label': '📊 Relatório',
                    'command': self._criar_relatorio,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#FF9800', '#F57C00'),
                    'hover_color': ('#F57C00', '#EF6C00'),
                    'width': 110
                },
                {
                    'label': '🗑️ Apagar',
                    'command': self._apagar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#F44336', '#C62828'),
                    'hover_color': ('#D32F2F', '#B71C1C'),
                    'width': 100
                }
            ]

        # Para context menu (ações contextuais baseadas em estado)
        boletim = data.get('_boletim')
        if not boletim:
            return []

        items = [
            {'label': '✏️ Editar', 'command': lambda: self.editar_boletim(data)},
            {'label': '📋 Duplicar', 'command': lambda: self._duplicar_from_context(boletim)},
            {'separator': True},
        ]

        # Ação depende do estado
        if boletim.estado == EstadoBoletim.PENDENTE:
            items.append({'label': '✅ Marcar como Pago', 'command': lambda: self._marcar_pago_from_context(boletim)})
        else:  # PAGO
            items.append({'label': '⏪ Voltar a Pendente', 'command': lambda: self._marcar_pendente_from_context(boletim)})

        items.append({'separator': True})
        items.append({'label': '🗑️ Apagar', 'command': lambda: self._apagar_from_context(boletim)})

        return items

    # ===== OPTIONAL METHODS =====

    def toolbar_slot(self, parent):
        """Create custom toolbar with filters and config button"""
        # Frame principal
        toolbar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar_frame.pack(fill="x", padx=0, pady=(0, 10))

        # Row 1: Filtros + botão config
        filters_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        filters_frame.pack(fill="x")

        # Sócio filter
        ctk.CTkLabel(
            filters_frame,
            text="Sócio:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.socio_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Todos", "BA", "RR"],
            command=lambda _: self.refresh_data(),
            width=150
        )
        self.socio_filter.set(self.filtro_inicial_socio or "Todos")
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
            command=lambda _: self.refresh_data(),
            width=120
        )
        self.estado_filter.set(self.filtro_inicial_estado or "Todos")
        self.estado_filter.pack(side="left", padx=(0, 20))

        # Config button (valores de referência)
        config_btn = ctk.CTkButton(
            filters_frame,
            text="⚙️",
            command=self.abrir_valores_referencia,
            width=35,
            height=35,
            font=ctk.CTkFont(size=16),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        config_btn.pack(side="left")

    def on_add_click(self):
        """Handle add button click"""
        self.abrir_formulario(boletim=None)

    def on_item_double_click(self, data: dict):
        """Handle table row double-click (editar)"""
        boletim = data.get('_boletim')
        if boletim:
            self.abrir_formulario(boletim)

    def calculate_selection_total(self, selected_data: List[Dict[str, Any]]) -> float:
        """Calculate total value of selected boletins"""
        return sum(item.get('valor', 0) for item in selected_data)

    # ===== BULK OPERATION METHODS FOR ACTION BAR =====

    def _editar_selecionado(self):
        """Edita boletim selecionado"""
        selected = self.get_selected_data()
        if selected and len(selected) == 1:
            self.on_item_double_click(selected[0])

    def _duplicar_selecionado(self):
        """Duplica boletim selecionado (APENAS 1)"""
        selected = self.get_selected_data()
        if not selected or len(selected) != 1:
            return

        boletim = selected[0].get('_boletim')
        if not boletim:
            return

        try:
            # Confirmar
            resposta = messagebox.askyesno(
                "Duplicar Boletim",
                f"Duplicar boletim {boletim.numero}?\n\n"
                f"Todas as deslocações serão copiadas.\n"
                f"O novo boletim abrirá em modo edição."
            )

            if not resposta:
                return

            # Duplicar
            sucesso, novo_boletim, erro = self.manager.duplicar_boletim(boletim.id)

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Boletim duplicado como {novo_boletim.numero}")
                self.abrir_formulario(novo_boletim)
            else:
                messagebox.showerror("Erro", erro or "Erro ao duplicar boletim")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao duplicar: {str(e)}")

    def _pagar_selecionados(self):
        """Marca boletins selecionados como pagos"""
        selected = self.get_selected_data()
        if not selected:
            return

        # Filtrar apenas não pagos
        unpaid = [b.get('_boletim') for b in selected
                  if b.get('_boletim') and b.get('_boletim').estado != EstadoBoletim.PAGO]

        if not unpaid:
            messagebox.showinfo("Info", "Todos já estão pagos.")
            return

        # Confirmar
        if not messagebox.askyesno(
            "Confirmar",
            f"Marcar {len(unpaid)} boletim(ns) como pago(s)?\n\n"
            f"Data: {date.today().strftime('%Y-%m-%d')}"
        ):
            return

        erros = []
        for boletim in unpaid:
            sucesso, erro = self.manager.marcar_como_pago(boletim.id)
            if not sucesso:
                erros.append(f"{boletim.numero}: {erro}")

        if not erros:
            self.refresh_data()
            messagebox.showinfo("Sucesso", f"{len(unpaid)} boletim(ns) marcado(s) como pago")
        else:
            messagebox.showerror("Erro", "\n".join(erros))
            self.refresh_data()

    def _criar_relatorio(self):
        """Cria relatório para boletins selecionados"""
        selected = self.get_selected_data()
        if not selected:
            return

        boletim_ids = [item.get('id') for item in selected if item.get('id')]

        # Navigate to Relatorios tab
        main_window = self.master.master
        if hasattr(main_window, 'show_relatorios'):
            main_window.show_relatorios(boletim_ids=boletim_ids)
        else:
            messagebox.showerror("Erro", "Não foi possível navegar para Relatórios")

    def _apagar_selecionados(self):
        """Apaga boletins selecionados"""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"Apagar {num} boletim(ns)?\n\n"
            f"⚠️ Esta ação não pode ser desfeita."
        ):
            return

        sucessos = 0
        erros = []

        for data in selected:
            boletim = data.get('_boletim')
            if boletim:
                sucesso, erro = self.manager.apagar(boletim.id)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{boletim.numero}: {erro}")

        if sucessos > 0:
            msg = f"✅ {sucessos} boletim(ns) apagado(s)!"
            if erros:
                msg += f"\n\n⚠️ {len(erros)} erro(s)"
            messagebox.showinfo("Resultado", msg)
        else:
            messagebox.showerror("Erro", "\n".join(erros[:5]))

        self.refresh_data()

    # ===== HELPER METHODS (MANTER) =====

    def get_estado_color(self, estado: EstadoBoletim) -> tuple:
        """Get color for estado (returns tuple: light, dark mode) - Opção 3 Agora Inspired"""
        color_map = {
            EstadoBoletim.PENDENTE: ("#FFE5D0", "#8B4513"),  # Laranja pastel - atenção
            EstadoBoletim.PAGO: ("#E8F5E0", "#4A7028")        # Verde pastel - positivo
        }
        return color_map.get(estado, ("#E0E0E0", "#4A4A4A"))

    def on_new_item(self):
        """Ação do botão 'Novo' - abre formulário para criar novo boletim"""
        self.abrir_formulario(None)

    def abrir_formulario(self, boletim=None):
        """Navigate to boletim_form screen for create/edit"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            if boletim:
                main_window.show_screen("boletim_form", boletim_id=boletim.id)
            else:
                main_window.show_screen("boletim_form", boletim_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível abrir formulário")

    def editar_boletim(self, data: dict):
        """Edit boletim (triggered by double-click or context menu)"""
        boletim = data.get('_boletim')
        if boletim:
            self.abrir_formulario(boletim)

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

    # ===== CONTEXT MENU HELPERS =====

    def _duplicar_from_context(self, boletim):
        """Duplica boletim a partir do menu de contexto"""
        try:
            # Confirm duplication
            resposta = messagebox.askyesno(
                "Duplicar Boletim",
                f"Duplicar boletim {boletim.numero}?\n\n"
                f"Todas as deslocações serão copiadas.\n"
                f"O novo boletim abrirá em modo edição."
            )

            if not resposta:
                return

            # Duplicate
            sucesso, novo_boletim, erro = self.manager.duplicar_boletim(boletim.id)

            if sucesso:
                # Reload list
                self.refresh_data()

                # Open new boletim for editing
                messagebox.showinfo("Sucesso", f"Boletim duplicado como {novo_boletim.numero}")
                self.abrir_formulario(novo_boletim)

            else:
                messagebox.showerror("Erro", erro or "Erro ao duplicar boletim")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao duplicar boletim: {str(e)}")

    def _marcar_pago_from_context(self, boletim):
        """Marca boletim como pago a partir do menu de contexto"""
        try:
            # Confirm action
            resposta = messagebox.askyesno(
                "Marcar como Pago",
                f"Marcar boletim {boletim.numero} como pago?\n\n"
                f"Data de pagamento será definida como hoje ({date.today().strftime('%Y-%m-%d')})."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.marcar_como_pago(boletim.id)

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Boletim {boletim.numero} marcado como pago")
            else:
                messagebox.showerror("Erro", erro or "Erro ao marcar como pago")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como pago: {str(e)}")

    def _marcar_pendente_from_context(self, boletim):
        """Marca boletim como pendente a partir do menu de contexto"""
        try:
            # Confirm action
            resposta = messagebox.askyesno(
                "Voltar a Pendente",
                f"Marcar boletim {boletim.numero} como pendente?\n\n"
                f"Data de pagamento será removida."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.marcar_como_pendente(boletim.id)

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Boletim {boletim.numero} marcado como pendente")
            else:
                messagebox.showerror("Erro", erro or "Erro ao marcar como pendente")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como pendente: {str(e)}")

    def _apagar_from_context(self, boletim):
        """Apaga boletim a partir do menu de contexto"""
        try:
            # Confirm deletion
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja apagar o boletim {boletim.numero}?\n\n"
                f"Esta ação não pode ser desfeita."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.apagar(boletim.id)

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Boletim {boletim.numero} apagado com sucesso")
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar boletim")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao apagar boletim: {str(e)}")

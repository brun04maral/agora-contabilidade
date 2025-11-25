# -*- coding: utf-8 -*-
"""
Tela de Orçamentos - Gestão de orçamentos (Cliente e Empresa)
"""
import customtkinter as ctk
import tkinter as tk
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from logic.clientes import ClientesManager
from ui.components.base_screen import BaseScreen
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from tkinter import messagebox
from database.models.orcamento import Orcamento
from assets.resources import get_icon, ORCAMENTOS


class OrcamentosScreen(BaseScreen):
    """
    Tela de gestão de Orçamentos
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        filtro_status: Optional[str] = None,
        filtro_cliente_id: Optional[int] = None,
        **kwargs
    ):
        self.db_session = db_session
        self.manager = OrcamentoManager(db_session)
        self.filtro_status_inicial = filtro_status
        self.filtro_cliente_id_inicial = filtro_cliente_id

        # Initialize filter widgets (created in toolbar_slot)
        self.search_entry = None
        self.status_combo = None
        self.stats_label = None

        # Call parent __init__ (this will call abstract methods)
        super().__init__(parent, db_session, **kwargs)

    # ===== ABSTRACT METHODS FROM BaseScreen =====

    def get_screen_title(self) -> str:
        """Return screen title"""
        return "Orçamentos"

    def get_screen_icon(self):
        """Return screen icon (PIL Image or None)"""
        return get_icon(ORCAMENTOS, size=(28, 28))

    def get_table_columns(self) -> List[Dict[str, Any]]:
        """Return table column definitions"""
        return [
            {"key": "codigo", "label": "Código", "width": 280},
            {"key": "cliente", "label": "Cliente", "width": 220},
            {"key": "data_criacao", "label": "Data Criação", "width": 120},
            {"key": "valor_total", "label": "Valor Total", "width": 120},
            {"key": "status", "label": "Status", "width": 120},
        ]

    def load_data(self) -> List[Dict[str, Any]]:
        """Load orçamentos from database and return as list of dicts"""
        # Get filters
        pesquisa = self.search_entry.get().strip() if self.search_entry else None

        filtro_status = None
        if self.status_combo:
            filtro_status = self.status_combo.get()
            if filtro_status == "Todos":
                filtro_status = None

        # Load orcamentos
        orcamentos = self.manager.listar_orcamentos(
            filtro_status=filtro_status,
            filtro_cliente_id=self.filtro_cliente_id_inicial,
            pesquisa=pesquisa
        )

        # Defensive: handle None or empty results
        if orcamentos is None:
            orcamentos = []

        # Prepare data for table
        data = []
        for orc in orcamentos:
            if orc is None:
                continue  # Skip None values
            cliente_nome = orc.cliente.nome if orc.cliente else "N/A"
            valor_str = f"{float(orc.valor_total or 0):.2f}€" if orc.valor_total else "0.00€"
            data_str = orc.data_criacao.strftime("%Y-%m-%d") if orc.data_criacao else "N/A"

            data.append({
                "id": orc.id,
                "codigo": orc.codigo or "",
                "cliente": cliente_nome,
                "data_criacao": data_str,
                "valor_total": valor_str,
                "status": orc.status or "rascunho",
                "_orcamento": orc,  # Store full object for context menu
            })

        # Update statistics
        self.atualizar_estatisticas()

        return data

    def get_context_menu_items(self, data: dict) -> List[Dict[str, Any]]:
        """
        Define ações do context menu e barra de ações.

        Args:
            data: Dict com dados da linha (vazio {} quando criar barra de ações)
        """
        # Para barra de ações (data vazio): retorna TODAS as ações possíveis
        if not data or '_orcamento' not in data:
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
                    'label': '👁️ Visualizar',
                    'command': self._visualizar_selecionado,
                    'min_selection': 1,
                    'max_selection': 1,
                    'fg_color': ('#00BCD4', '#0097A7'),
                    'hover_color': ('#0097A7', '#00838F'),
                    'width': 120
                },
                {
                    'label': '📋 Duplicar',
                    'command': self._duplicar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#9C27B0', '#7B1FA2'),
                    'hover_color': ('#7B1FA2', '#6A1B9A'),
                    'width': 110
                },
                {
                    'label': '✅ Aprovar',
                    'command': self._aprovar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#4CAF50', '#388E3C'),
                    'hover_color': ('#388E3C', '#2E7D32'),
                    'width': 110
                },
                {
                    'label': '💰 Marcar Pago',
                    'command': self._pagar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#4CAF50', '#388E3C'),
                    'hover_color': ('#388E3C', '#2E7D32'),
                    'width': 130
                },
                {
                    'label': '⛔ Anular',
                    'command': self._anular_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#FF9800', '#F57C00'),
                    'hover_color': ('#F57C00', '#EF6C00'),
                    'width': 100
                },
                {
                    'label': '🗑️ Apagar',
                    'command': self._apagar_selecionados,
                    'min_selection': 1,
                    'max_selection': None,
                    'fg_color': ('#F44336', '#D32F2F'),
                    'hover_color': ('#D32F2F', '#C62828'),
                    'width': 100
                }
            ]

        # Para context menu (data com orçamento específico): ações contextuais
        orcamento = data.get('_orcamento')
        if not orcamento:
            return []

        status = orcamento.status or 'rascunho'

        items = [
            {'label': '👁️ Visualizar', 'command': lambda: self._visualizar_from_context(orcamento)},
            {'label': '✏️ Editar', 'command': lambda: self.on_item_double_click(data)},
            {'label': '📋 Duplicar', 'command': lambda: self._duplicar_from_context(orcamento)},
            {'separator': True},
        ]

        # Ações baseadas no status
        if status == 'rascunho':
            items.append({'label': '✅ Marcar como Aprovado', 'command': lambda: self._marcar_aprovado_from_context(orcamento)})
        elif status == 'aprovado':
            items.append({'label': '💰 Marcar como Pago', 'command': lambda: self._marcar_pago_from_context(orcamento)})
            items.append({'label': '⏪ Voltar a Rascunho', 'command': lambda: self._voltar_rascunho_from_context(orcamento)})
        elif status == 'pago':
            items.append({'label': '⏪ Voltar a Aprovado', 'command': lambda: self._marcar_aprovado_from_context(orcamento)})

        # Anular (se não estiver já anulado)
        if status != 'anulado':
            items.append({'separator': True})
            items.append({'label': '⛔ Anular Orçamento', 'command': lambda: self._anular_from_context(orcamento)})

        items.append({'separator': True})
        items.append({'label': '🗑️ Apagar', 'command': lambda: self._apagar_from_context(orcamento)})

        return items

    def on_add_click(self):
        """Handle add button click"""
        # Hierarchy: self (OrcamentosScreen) -> master (content_frame) -> master (MainWindow)
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("orcamento_form", orcamento_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível navegar para o formulário de orçamento")

    def on_item_double_click(self, data: dict):
        """Handle table row double-click (editar)"""
        orcamento_id = data.get("id")
        if not orcamento_id:
            return

        # Hierarchy: self (OrcamentosScreen) -> master (content_frame) -> master (MainWindow)
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("orcamento_form", orcamento_id=orcamento_id)
        else:
            messagebox.showerror("Erro", "Não foi possível navegar para o formulário de orçamento")

    def toolbar_slot(self, parent):
        """Create custom toolbar with filters and statistics"""
        # Filters frame
        filters_frame = ctk.CTkFrame(parent, fg_color="transparent")
        filters_frame.pack(fill="x", padx=0, pady=(0, 10))

        # Search
        search_label = ctk.CTkLabel(
            filters_frame,
            text="🔍 Pesquisar:",
            font=ctk.CTkFont(size=13)
        )
        search_label.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            filters_frame,
            placeholder_text="Código ou descrição...",
            width=250,
            height=35
        )
        self.search_entry.pack(side="left", padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        # Status filter
        status_label = ctk.CTkLabel(
            filters_frame,
            text="Status:",
            font=ctk.CTkFont(size=13)
        )
        status_label.pack(side="left", padx=(0, 10))

        self.status_combo = ctk.CTkComboBox(
            filters_frame,
            values=self.manager.obter_status(),
            width=150,
            height=35,
            command=lambda _: self.refresh_data()
        )
        self.status_combo.set(self.filtro_status_inicial or "Todos")
        self.status_combo.pack(side="left", padx=(0, 20))

        # Statistics frame
        stats_frame = ctk.CTkFrame(parent, corner_radius=8)
        stats_frame.pack(fill="x", pady=(0, 10))

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Carregando estatísticas...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.stats_label.pack(pady=10)

    def calculate_selection_total(self, selected_data: List[Dict[str, Any]]) -> float:
        """Calculate total value of selected orçamentos"""
        total = 0.0
        for data in selected_data:
            orcamento = data.get('_orcamento')
            if orcamento and orcamento.valor_total:
                total += float(orcamento.valor_total)
        return total

    # ===== BULK OPERATION METHODS FOR ACTION BAR =====

    def _editar_selecionado(self):
        """Edita orçamento selecionado."""
        selected = self.get_selected_data()
        if not selected or len(selected) != 1:
            return
        self.on_item_double_click(selected[0])

    def _visualizar_selecionado(self):
        """Visualiza orçamento selecionado."""
        selected = self.get_selected_data()
        if not selected or len(selected) != 1:
            return

        orcamento = selected[0].get('_orcamento')
        if orcamento:
            self._mostrar_visualizacao(orcamento)

    def _duplicar_selecionados(self):
        """Duplica orçamentos selecionados."""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        msg = f"Duplicar {num} orçamento(s)?" if num > 1 else f"Duplicar orçamento '{selected[0]['codigo']}'?"

        if not messagebox.askyesno("Confirmar Duplicação", msg):
            return

        sucessos = 0
        erros = []
        novos = []

        for data in selected:
            sucesso, novo, erro = self.manager.duplicar_orcamento(data["id"])
            if sucesso:
                sucessos += 1
                novos.append(novo.codigo)
            else:
                erros.append(f"{data['codigo']}: {erro}")

        # Mostrar resultado
        if sucessos > 0:
            self.refresh_data()
            if len(erros) == 0:
                msg = f"{sucessos} orçamento(s) duplicado(s):\n" + "\n".join(novos)
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showwarning(
                    "Parcialmente Concluído",
                    f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5])
                )
        elif erros:
            messagebox.showerror("Erro", "Erros:\n" + "\n".join(erros[:5]))

    def _aprovar_selecionados(self):
        """Aprova orçamentos selecionados (rascunho → aprovado)."""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        resposta = messagebox.askyesno(
            "Aprovar Orçamentos",
            f"Aprovar {num} orçamento(s)?\n\n"
            f"Status passará para APROVADO.",
            icon='question'
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            orcamento = data.get('_orcamento')
            if orcamento and orcamento.status == 'rascunho':
                sucesso, erro = self.manager.mudar_status(orcamento.id, 'aprovado')
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{orcamento.codigo}: {erro}")

        # Mostrar resultado
        if sucessos > 0:
            self.refresh_data()
            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{sucessos} orçamento(s) aprovado(s)")
            else:
                messagebox.showwarning(
                    "Parcialmente Concluído",
                    f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5])
                )
        elif erros:
            messagebox.showerror("Erro", "Erros:\n" + "\n".join(erros[:5]))

    def _pagar_selecionados(self):
        """Marca orçamentos selecionados como pagos (aprovado → pago)."""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        resposta = messagebox.askyesno(
            "Marcar como Pago",
            f"Marcar {num} orçamento(s) como pago?\n\n"
            f"Status passará para PAGO.",
            icon='question'
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            orcamento = data.get('_orcamento')
            if orcamento and orcamento.status == 'aprovado':
                sucesso, erro = self.manager.mudar_status(orcamento.id, 'pago')
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{orcamento.codigo}: {erro}")

        # Mostrar resultado
        if sucessos > 0:
            self.refresh_data()
            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{sucessos} orçamento(s) marcado(s) como pago")
            else:
                messagebox.showwarning(
                    "Parcialmente Concluído",
                    f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5])
                )
        elif erros:
            messagebox.showerror("Erro", "Erros:\n" + "\n".join(erros[:5]))

    def _anular_selecionados(self):
        """Anula orçamentos selecionados."""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        resposta = messagebox.askyesno(
            "Anular Orçamentos",
            f"Anular {num} orçamento(s)?\n\n"
            f"⚠️ Orçamentos anulados não entram nos cálculos.",
            icon='warning'
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            orcamento = data.get('_orcamento')
            if orcamento:
                sucesso, erro = self.manager.mudar_status(orcamento.id, 'anulado')
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{orcamento.codigo}: {erro}")

        # Mostrar resultado
        if sucessos > 0:
            self.refresh_data()
            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{sucessos} orçamento(s) anulado(s)")
            else:
                messagebox.showwarning(
                    "Parcialmente Concluído",
                    f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5])
                )
        elif erros:
            messagebox.showerror("Erro", "Erros:\n" + "\n".join(erros[:5]))

    def _apagar_selecionados(self):
        """Apaga orçamentos selecionados."""
        selected = self.get_selected_data()
        if not selected:
            return

        num = len(selected)
        resposta = messagebox.askyesno(
            "Apagar Orçamentos",
            f"Apagar {num} orçamento(s)?\n\n"
            f"⚠️ Esta ação é irreversível!",
            icon='warning'
        )

        if not resposta:
            return

        sucessos = 0
        erros = []

        for data in selected:
            orcamento = data.get('_orcamento')
            if orcamento:
                sucesso, erro = self.manager.eliminar_orcamento(orcamento.id)
                if sucesso:
                    sucessos += 1
                else:
                    erros.append(f"{orcamento.codigo}: {erro}")

        # Mostrar resultado
        if sucessos > 0:
            self.refresh_data()
            if len(erros) == 0:
                messagebox.showinfo("Sucesso", f"{sucessos} orçamento(s) apagado(s)")
            else:
                messagebox.showwarning(
                    "Parcialmente Concluído",
                    f"{sucessos} sucesso(s), {len(erros)} erro(s):\n" + "\n".join(erros[:5])
                )
        elif erros:
            messagebox.showerror("Erro", "Erros:\n" + "\n".join(erros[:5]))

    # ===== HELPER METHODS =====

    def atualizar_estatisticas(self):
        """Update statistics display"""
        if not self.stats_label:
            return

        try:
            stats = self.manager.estatisticas()

            total = stats['total']
            valor_aprovado = stats['valor_total_aprovado']

            stats_text = f"📊 Total: {total} orçamentos"
            if valor_aprovado > 0:
                stats_text += f" | 💰 Valor Aprovado: {valor_aprovado:.2f}€"

            # Status breakdown
            por_status = stats.get('por_status', {})
            if por_status:
                status_parts = []
                for status, count in por_status.items():
                    status_parts.append(f"{status}: {count}")
                stats_text += f" | Status: {', '.join(status_parts)}"

            self.stats_label.configure(text=stats_text)

        except Exception as e:
            self.stats_label.configure(text=f"⚠️ Erro ao carregar estatísticas: {str(e)}")

    def abrir_formulario(self, orcamento):
        """
        Compatibility method - opens edit form for an orcamento

        Args:
            orcamento: Orcamento object or ID
        """
        # Extract ID if object
        if hasattr(orcamento, 'id'):
            orcamento_id = orcamento.id
        else:
            orcamento_id = orcamento

        # Navigate to form
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("orcamento_form", orcamento_id=orcamento_id)
        else:
            messagebox.showerror("Erro", "Não foi possível navegar para o formulário de orçamento")

    # ===== CONTEXT MENU HELPERS =====

    def _visualizar_from_context(self, orcamento):
        """Visualiza orçamento a partir do menu de contexto"""
        self._mostrar_visualizacao(orcamento)

    def _duplicar_from_context(self, orcamento):
        """Duplica orçamento a partir do menu de contexto"""
        try:
            # Confirmar duplicação
            resposta = messagebox.askyesno(
                "Duplicar Orçamento",
                f"Duplicar orçamento {orcamento.codigo}?\n\n"
                f"Cliente: {orcamento.cliente.nome if orcamento.cliente else '-'}\n"
                f"Valor: €{float(orcamento.valor_total or 0):.2f}\n\n"
                f"O novo orçamento será criado com status RASCUNHO\n"
                f"e datas resetadas."
            )

            if not resposta:
                return

            # Duplicar
            sucesso, novo_orcamento, erro = self.manager.duplicar_orcamento(orcamento.id)

            if sucesso:
                # Recarregar lista
                self.refresh_data()

                # Abrir novo orçamento para edição
                messagebox.showinfo(
                    "Sucesso",
                    f"Orçamento duplicado como {novo_orcamento.codigo}\n\n"
                    f"Abrindo para edição..."
                )
                self.abrir_formulario(novo_orcamento)

            else:
                messagebox.showerror("Erro", erro or "Erro ao duplicar orçamento")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao duplicar orçamento: {str(e)}")

    def _marcar_aprovado_from_context(self, orcamento):
        """Marca orçamento como APROVADO a partir do menu de contexto"""
        try:
            resposta = messagebox.askyesno(
                "Marcar como Aprovado",
                f"Marcar orçamento {orcamento.codigo} como aprovado?\n\n"
                f"O orçamento passa para status APROVADO."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_status(orcamento.id, 'aprovado')

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Orçamento {orcamento.codigo} marcado como aprovado")
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar status")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como aprovado: {str(e)}")

    def _marcar_pago_from_context(self, orcamento):
        """Marca orçamento como PAGO a partir do menu de contexto"""
        try:
            resposta = messagebox.askyesno(
                "Marcar como Pago",
                f"Marcar orçamento {orcamento.codigo} como pago?\n\n"
                f"O orçamento passa para status PAGO."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_status(orcamento.id, 'pago')

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Orçamento {orcamento.codigo} marcado como pago")
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar status")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar como pago: {str(e)}")

    def _voltar_rascunho_from_context(self, orcamento):
        """Volta orçamento para RASCUNHO a partir do menu de contexto"""
        try:
            resposta = messagebox.askyesno(
                "Voltar a Rascunho",
                f"Voltar orçamento {orcamento.codigo} para rascunho?\n\n"
                f"O orçamento volta para status RASCUNHO."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_status(orcamento.id, 'rascunho')

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Orçamento {orcamento.codigo} voltou a rascunho")
            else:
                messagebox.showerror("Erro", erro or "Erro ao mudar status")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao voltar a rascunho: {str(e)}")

    def _anular_from_context(self, orcamento):
        """Anula orçamento a partir do menu de contexto"""
        try:
            resposta = messagebox.askyesno(
                "Anular Orçamento",
                f"Anular orçamento {orcamento.codigo}?\n\n"
                f"⚠️ Esta ação marca o orçamento como ANULADO."
            )

            if not resposta:
                return

            sucesso, erro = self.manager.mudar_status(orcamento.id, 'anulado')

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Orçamento {orcamento.codigo} anulado")
            else:
                messagebox.showerror("Erro", erro or "Erro ao anular")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao anular orçamento: {str(e)}")

    def _apagar_from_context(self, orcamento):
        """Apaga orçamento a partir do menu de contexto"""
        try:
            resposta = messagebox.askyesno(
                "Apagar Orçamento",
                f"Apagar orçamento {orcamento.codigo}?\n\n"
                f"⚠️ Esta ação é irreversível!"
            )

            if not resposta:
                return

            sucesso, erro = self.manager.eliminar_orcamento(orcamento.id)

            if sucesso:
                self.refresh_data()
                messagebox.showinfo("Sucesso", f"Orçamento {orcamento.codigo} apagado")
            else:
                messagebox.showerror("Erro", erro or "Erro ao apagar")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao apagar orçamento: {str(e)}")

    def _mostrar_visualizacao(self, orcamento):
        """Mostra visualização do orçamento (método auxiliar)"""
        # Reutilizar lógica existente de visualizar_orcamento
        # Criar popup de visualização
        popup = ctk.CTkToplevel(self)
        popup.title(f"Orçamento {orcamento.codigo}")
        popup.geometry("600x700")
        popup.transient(self)
        popup.grab_set()

        # Scroll frame
        scroll_frame = ctk.CTkScrollableFrame(popup)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkLabel(
            scroll_frame,
            text=f"Orçamento {orcamento.codigo}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=(0, 20))

        # Basic info
        info_frame = ctk.CTkFrame(scroll_frame)
        info_frame.pack(fill="x", pady=(0, 20))

        info_data = [
            ("Owner", orcamento.owner or "N/A"),
            ("Status", orcamento.status or "rascunho"),
            ("Cliente", orcamento.cliente.nome if orcamento.cliente else "N/A"),
            ("Data Criação", orcamento.data_criacao.strftime("%Y-%m-%d") if orcamento.data_criacao else "N/A"),
            ("Data Evento", orcamento.data_evento or "N/A"),
            ("Local Evento", orcamento.local_evento or "N/A"),
        ]

        for label_text, value_text in info_data:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)

            label = ctk.CTkLabel(
                row,
                text=f"{label_text}:",
                font=ctk.CTkFont(weight="bold"),
                width=120,
                anchor="w"
            )
            label.pack(side="left")

            value = ctk.CTkLabel(
                row,
                text=str(value_text),
                anchor="w"
            )
            value.pack(side="left", fill="x", expand=True)

        # Valor total
        total_frame = ctk.CTkFrame(scroll_frame)
        total_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            total_frame,
            text=f"Valor Total: €{float(orcamento.valor_total or 0):.2f}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        ).pack(pady=10)

        # Botão fechar
        ctk.CTkButton(
            scroll_frame,
            text="Fechar",
            command=popup.destroy,
            width=100
        ).pack(pady=20)


# -*- coding: utf-8 -*-
"""
Tela de Orçamentos - Gestão de orçamentos (Cliente e Empresa)
"""
import customtkinter as ctk
import tkinter as tk
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from logic.clientes import ClientesManager
from ui.components.data_table_v2 import DataTableV2
from typing import Optional
from datetime import date, datetime
from tkinter import messagebox
from database.models.orcamento import Orcamento
from assets.resources import get_icon, ORCAMENTOS


class OrcamentosScreen(ctk.CTkFrame):
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
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = OrcamentoManager(db_session)
        self.filtro_status_inicial = filtro_status
        self.filtro_cliente_id_inicial = filtro_cliente_id

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

        # Load data
        self.carregar_orcamentos()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title with PNG icon
        icon_pil = get_icon(ORCAMENTOS, size=(28, 28))
        if icon_pil:
            icon_ctk = ctk.CTkImage(
                light_image=icon_pil,
                dark_image=icon_pil,
                size=(28, 28)
            )
            title_label = ctk.CTkLabel(
                header_frame,
                image=icon_ctk,
                text=" Orçamentos",
                compound="left",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        else:
            title_label = ctk.CTkLabel(
                header_frame,
                text="📋 Orçamentos",
                font=ctk.CTkFont(size=28, weight="bold")
            )
        title_label.pack(side="left")

        # Action buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar",
            command=self.carregar_orcamentos,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=5)

        # Add button
        add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Novo Orçamento",
            command=self.adicionar_orcamento,
            width=150,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_btn.pack(side="left", padx=5)

        # Filters frame
        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.pack(fill="x", padx=30, pady=(0, 20))

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
        self.search_entry.bind("<KeyRelease>", lambda e: self.carregar_orcamentos())

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
            command=lambda _: self.carregar_orcamentos()
        )
        self.status_combo.set(self.filtro_status_inicial or "Todos")
        self.status_combo.pack(side="left", padx=(0, 20))

        # Statistics frame
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Carregando estatísticas...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.stats_label.pack(pady=10)

        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Create table
        columns = [
            {"key": "codigo", "label": "Código", "width": 280},
            {"key": "cliente", "label": "Cliente", "width": 220},
            {"key": "data_criacao", "label": "Data Criação", "width": 120},
            {"key": "valor_total", "label": "Valor Total", "width": 120},
            {"key": "status", "label": "Status", "width": 120},
        ]

        self.table = DataTableV2(
            table_frame,
            columns=columns,
            on_row_double_click=self.editar_orcamento,
            on_selection_change=self.on_selection_change,
            on_row_right_click=self.show_context_menu
        )
        self.table.pack(fill="both", expand=True)

        # Bottom action buttons
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=30, pady=(10, 30))

        # Edit button (hidden by default)
        self.edit_btn = ctk.CTkButton(
            bottom_frame,
            text="✏️ Editar",
            command=self.editar_orcamento,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.edit_btn.pack(side="left", padx=(0, 10))
        self.edit_btn.pack_forget()  # Hide initially

        # View button (hidden by default)
        self.view_btn = ctk.CTkButton(
            bottom_frame,
            text="👁️ Visualizar",
            command=self.visualizar_orcamento,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        self.view_btn.pack(side="left", padx=(0, 10))
        self.view_btn.pack_forget()  # Hide initially

        # Duplicate button (hidden by default)
        self.duplicate_btn = ctk.CTkButton(
            bottom_frame,
            text="📋 Duplicar",
            command=self.duplicar_selecionados,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        )
        self.duplicate_btn.pack(side="left", padx=(0, 10))
        self.duplicate_btn.pack_forget()  # Hide initially

        # Delete button (hidden by default)
        self.delete_btn = ctk.CTkButton(
            bottom_frame,
            text="🗑️ Eliminar",
            command=self.eliminar_orcamento,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#f44336",
            hover_color="#da190b"
        )
        self.delete_btn.pack(side="left", padx=(0, 10))
        self.delete_btn.pack_forget()  # Hide initially

    def on_selection_change(self, selected_rows):
        """Handle table selection change"""
        if len(selected_rows) == 1:
            # Show all action buttons
            self.edit_btn.pack(side="left", padx=(0, 10))
            self.view_btn.pack(side="left", padx=(0, 10))
            self.duplicate_btn.pack(side="left", padx=(0, 10))
            self.delete_btn.pack(side="left", padx=(0, 10))
        elif len(selected_rows) > 1:
            # Hide edit and view, show duplicate and delete
            self.edit_btn.pack_forget()
            self.view_btn.pack_forget()
            self.duplicate_btn.pack(side="left", padx=(0, 10))
            self.delete_btn.pack(side="left", padx=(0, 10))
        else:
            # Hide all
            self.edit_btn.pack_forget()
            self.view_btn.pack_forget()
            self.duplicate_btn.pack_forget()
            self.delete_btn.pack_forget()

    def carregar_orcamentos(self):
        """Load orcamentos from database"""
        # Get filters
        pesquisa = self.search_entry.get().strip() or None

        filtro_status = self.status_combo.get()
        if filtro_status == "Todos":
            filtro_status = None

        # Load orcamentos
        orcamentos = self.manager.listar_orcamentos(
            filtro_status=filtro_status,
            filtro_cliente_id=self.filtro_cliente_id_inicial,
            pesquisa=pesquisa
        )

        # Prepare data for table
        data = []
        for orc in orcamentos:
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
            })

        # Update table
        self.table.set_data(data)

        # Update statistics
        self.atualizar_estatisticas()

    def atualizar_estatisticas(self):
        """Update statistics display"""
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

    def adicionar_orcamento(self):
        """Add new orcamento"""
        # Hierarchy: self (OrcamentosScreen) -> master (content_frame) -> master (MainWindow)
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("orcamento_form", orcamento_id=None)
        else:
            messagebox.showerror("Erro", "Não foi possível navegar para o formulário de orçamento")

    def editar_orcamento(self, data=None):
        """Edit selected orcamento"""
        if data:
            # Double click - data already provided
            orcamento_id = data["id"]
        else:
            # Button click - get from selection
            selected = self.table.get_selected_data()
            if not selected or len(selected) != 1:
                return
            orcamento_id = selected[0]["id"]

        # Hierarchy: self (OrcamentosScreen) -> master (content_frame) -> master (MainWindow)
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("orcamento_form", orcamento_id=orcamento_id)
        else:
            messagebox.showerror("Erro", "Não foi possível navegar para o formulário de orçamento")

    def visualizar_orcamento(self):
        """View selected orcamento details"""
        selected = self.table.get_selected_data()
        if not selected or len(selected) != 1:
            return

        orcamento_id = selected[0]["id"]
        orcamento = self.manager.obter_orcamento(orcamento_id)

        if not orcamento:
            from tkinter import messagebox
            messagebox.showerror("Erro", "Orçamento não encontrado!")
            return

        # Create view dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Orçamento: {orcamento.codigo}")
        dialog.geometry("900x700")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"900x700+{x}+{y}")

        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            scroll_frame,
            text=f"📋 {orcamento.codigo}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(0, 20))

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
                font=ctk.CTkFont(size=13, weight="bold"),
                width=120,
                anchor="w"
            )
            label.pack(side="left")

            value = ctk.CTkLabel(
                row,
                text=str(value_text),
                font=ctk.CTkFont(size=13),
                anchor="w"
            )
            value.pack(side="left", fill="x", expand=True)

        # Description
        if orcamento.descricao_proposta:
            desc_label = ctk.CTkLabel(
                scroll_frame,
                text="Descrição da Proposta:",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            desc_label.pack(fill="x", pady=(10, 5))

            desc_text = ctk.CTkTextbox(scroll_frame, height=80)
            desc_text.pack(fill="x", pady=(0, 20))
            desc_text.insert("1.0", orcamento.descricao_proposta)
            desc_text.configure(state="disabled")

        # Valores
        valores_frame = ctk.CTkFrame(scroll_frame)
        valores_frame.pack(fill="x", pady=(0, 20))

        valores_title = ctk.CTkLabel(
            valores_frame,
            text="💰 Valores",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        valores_title.pack(pady=(10, 10))

        if orcamento.total_parcial_1:
            parcial1 = ctk.CTkLabel(
                valores_frame,
                text=f"Total Parcial 1 (Serviços + Equipamento): {float(orcamento.total_parcial_1):.2f}€",
                font=ctk.CTkFont(size=13)
            )
            parcial1.pack(pady=2)

        if orcamento.total_parcial_2:
            parcial2 = ctk.CTkLabel(
                valores_frame,
                text=f"Total Parcial 2 (Despesas): {float(orcamento.total_parcial_2):.2f}€",
                font=ctk.CTkFont(size=13)
            )
            parcial2.pack(pady=2)

        if orcamento.valor_total:
            total = ctk.CTkLabel(
                valores_frame,
                text=f"TOTAL: {float(orcamento.valor_total):.2f}€",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#4CAF50"
            )
            total.pack(pady=5)

        # Secções e Items
        secoes = self.manager.obter_secoes(orcamento.id)
        if secoes:
            secoes_label = ctk.CTkLabel(
                scroll_frame,
                text="📑 Secções e Items",
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w"
            )
            secoes_label.pack(fill="x", pady=(20, 10))

            for secao in secoes:
                secao_frame = ctk.CTkFrame(scroll_frame)
                secao_frame.pack(fill="x", pady=5)

                secao_title = ctk.CTkLabel(
                    secao_frame,
                    text=f"▸ {secao.nome}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                )
                secao_title.pack(fill="x", padx=10, pady=5)

                # Items da secção
                items = self.manager.obter_itens(orcamento.id, secao.id)
                if items:
                    for item in items:
                        item_text = f"  • {item.descricao} - Qtd: {item.quantidade} x {item.dias} dias x {float(item.preco_unitario):.2f}€"
                        if item.desconto > 0:
                            item_text += f" (Desconto: {float(item.desconto*100):.0f}%)"
                        item_text += f" = {float(item.total):.2f}€"

                        item_label = ctk.CTkLabel(
                            secao_frame,
                            text=item_text,
                            font=ctk.CTkFont(size=12),
                            anchor="w",
                            text_color="gray"
                        )
                        item_label.pack(fill="x", padx=20, pady=2)

        # Close button
        close_btn = ctk.CTkButton(
            dialog,
            text="Fechar",
            command=dialog.destroy,
            width=120,
            height=35
        )
        close_btn.pack(pady=10)

    def eliminar_orcamento(self):
        """Delete selected orcamento(s)"""
        selected = self.table.get_selected_data()
        if not selected:
            return

        from tkinter import messagebox

        if len(selected) == 1:
            msg = f"Tem a certeza que deseja eliminar o orçamento '{selected[0]['codigo']}'?"
        else:
            msg = f"Tem a certeza que deseja eliminar {len(selected)} orçamentos?"

        if not messagebox.askyesno("Confirmar Eliminação", msg):
            return

        # Delete orcamentos
        erros = []
        for row in selected:
            sucesso, erro = self.manager.eliminar_orcamento(row["id"])
            if not sucesso:
                erros.append(f"{row['codigo']}: {erro}")

        if erros:
            messagebox.showerror(
                "Erro",
                f"Erro ao eliminar orçamentos:\n" + "\n".join(erros)
            )

        # Reload
        self.carregar_orcamentos()

    # ===== MENU DE CONTEXTO (RIGHT-CLICK) =====

    def show_context_menu(self, event, data: dict):
        """
        Mostra menu de contexto (right-click) para um orçamento

        Args:
            event: Evento do clique (para posição)
            data: Dados da linha clicada
        """
        orcamento_id = data.get('id')
        if not orcamento_id:
            return

        # Buscar orçamento completo
        orcamento = self.manager.obter_orcamento(orcamento_id)
        if not orcamento:
            return

        # Criar menu
        menu = tk.Menu(self, tearoff=0)

        # 👁️ Visualizar
        menu.add_command(
            label="👁️ Visualizar",
            command=lambda: self._visualizar_from_context(orcamento)
        )

        # ✏️ Editar
        menu.add_command(
            label="✏️ Editar",
            command=lambda: self._editar_from_context(orcamento)
        )

        # 📋 Duplicar
        menu.add_command(
            label="📋 Duplicar",
            command=lambda: self._duplicar_from_context(orcamento)
        )

        menu.add_separator()

        # Ações dependem do status atual
        status = orcamento.status or 'rascunho'

        if status == 'rascunho':
            menu.add_command(
                label="✅ Marcar como Aprovado",
                command=lambda: self._marcar_aprovado_from_context(orcamento)
            )
        elif status == 'aprovado':
            menu.add_command(
                label="💰 Marcar como Pago",
                command=lambda: self._marcar_pago_from_context(orcamento)
            )
            menu.add_command(
                label="⏪ Voltar a Rascunho",
                command=lambda: self._voltar_rascunho_from_context(orcamento)
            )
        elif status == 'pago':
            menu.add_command(
                label="⏪ Voltar a Aprovado",
                command=lambda: self._marcar_aprovado_from_context(orcamento)
            )

        # Anular (se não estiver já anulado)
        if status != 'anulado':
            menu.add_separator()
            menu.add_command(
                label="⛔ Anular Orçamento",
                command=lambda: self._anular_from_context(orcamento)
            )

        menu.add_separator()

        # 🗑️ Apagar
        menu.add_command(
            label="🗑️ Apagar",
            command=lambda: self._apagar_from_context(orcamento)
        )

        # Mostrar menu na posição do cursor
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _visualizar_from_context(self, orcamento):
        """Visualiza orçamento a partir do menu de contexto"""
        # Seleccionar na tabela e chamar visualizar
        self.table.clear_selection()
        # Chamar método existente
        self._mostrar_visualizacao(orcamento)

    def _editar_from_context(self, orcamento):
        """Edita orçamento a partir do menu de contexto"""
        self.abrir_formulario(orcamento)

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
                self.carregar_orcamentos()
                self.table.clear_selection()

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
                self.carregar_orcamentos()
                self.table.clear_selection()
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
                self.carregar_orcamentos()
                self.table.clear_selection()
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
                self.carregar_orcamentos()
                self.table.clear_selection()
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
                self.carregar_orcamentos()
                self.table.clear_selection()
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
                self.carregar_orcamentos()
                self.table.clear_selection()
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

    def duplicar_selecionados(self):
        """Duplica orçamentos selecionados (para barra inferior)"""
        selected = self.table.get_selected_data()
        if not selected:
            return

        if len(selected) == 1:
            msg = f"Duplicar orçamento '{selected[0]['codigo']}'?"
        else:
            msg = f"Duplicar {len(selected)} orçamentos?"

        if not messagebox.askyesno("Confirmar Duplicação", msg):
            return

        # Duplicar orçamentos
        erros = []
        novos = []
        for row in selected:
            sucesso, novo, erro = self.manager.duplicar_orcamento(row["id"])
            if sucesso:
                novos.append(novo.codigo)
            else:
                erros.append(f"{row['codigo']}: {erro}")

        if erros:
            messagebox.showerror(
                "Erro",
                f"Erro ao duplicar alguns orçamentos:\n" + "\n".join(erros)
            )

        if novos:
            messagebox.showinfo(
                "Sucesso",
                f"Orçamentos duplicados:\n" + "\n".join(novos)
            )

        # Reload
        self.carregar_orcamentos()


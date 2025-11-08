# -*- coding: utf-8 -*-
"""
Tela de Orçamentos - Gestão de orçamentos (frontend e backend)
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from logic.clientes import ClientesManager
from ui.components.data_table_v2 import DataTableV2
from typing import Optional
from datetime import date, datetime
from tkinter import messagebox
from database.models.orcamento import Orcamento


class OrcamentosScreen(ctk.CTkFrame):
    """
    Tela de gestão de Orçamentos
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        filtro_tipo: Optional[str] = None,
        filtro_status: Optional[str] = None,
        filtro_cliente_id: Optional[int] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = OrcamentoManager(db_session)
        self.filtro_tipo_inicial = filtro_tipo
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

        # Tipo filter
        tipo_label = ctk.CTkLabel(
            filters_frame,
            text="Tipo:",
            font=ctk.CTkFont(size=13)
        )
        tipo_label.pack(side="left", padx=(0, 10))

        self.tipo_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todos", "frontend", "backend"],
            width=150,
            height=35,
            command=lambda _: self.carregar_orcamentos()
        )
        self.tipo_combo.set(self.filtro_tipo_inicial or "Todos")
        self.tipo_combo.pack(side="left", padx=(0, 20))

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
            {"key": "codigo", "label": "Código", "width": 250},
            {"key": "versao", "label": "Versão", "width": 80},
            {"key": "tipo", "label": "Tipo", "width": 100},
            {"key": "cliente", "label": "Cliente", "width": 200},
            {"key": "data_criacao", "label": "Data Criação", "width": 120},
            {"key": "valor_total", "label": "Valor Total", "width": 120},
            {"key": "status", "label": "Status", "width": 120},
        ]

        self.table = DataTableV2(
            table_frame,
            columns=columns,
            on_row_double_click=self.editar_orcamento,
            on_selection_change=self.on_selection_change
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
            self.delete_btn.pack(side="left", padx=(0, 10))
        elif len(selected_rows) > 1:
            # Hide edit and view, show delete only
            self.edit_btn.pack_forget()
            self.view_btn.pack_forget()
            self.delete_btn.pack(side="left", padx=(0, 10))
        else:
            # Hide all
            self.edit_btn.pack_forget()
            self.view_btn.pack_forget()
            self.delete_btn.pack_forget()

    def carregar_orcamentos(self):
        """Load orcamentos from database"""
        # Get filters
        pesquisa = self.search_entry.get().strip() or None

        filtro_tipo = self.tipo_combo.get()
        if filtro_tipo == "Todos":
            filtro_tipo = None

        filtro_status = self.status_combo.get()
        if filtro_status == "Todos":
            filtro_status = None

        # Load orcamentos
        orcamentos = self.manager.listar_orcamentos(
            filtro_tipo=filtro_tipo,
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
                "versao": orc.versao or "-",
                "tipo": orc.tipo or "",
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
        dialog = OrcamentoDialog(self, self.manager, self.db_session)
        self.wait_window(dialog)
        if dialog.orcamento_criado:
            self.carregar_orcamentos()

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

        orcamento = self.manager.obter_orcamento(orcamento_id)

        if not orcamento:
            messagebox.showerror("Erro", "Orçamento não encontrado!")
            return

        dialog = OrcamentoDialog(self, self.manager, self.db_session, orcamento=orcamento)
        self.wait_window(dialog)
        if dialog.orcamento_atualizado:
            self.carregar_orcamentos()

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
            text=f"📋 {orcamento.codigo} {orcamento.versao or ''}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(0, 20))

        # Basic info
        info_frame = ctk.CTkFrame(scroll_frame)
        info_frame.pack(fill="x", pady=(0, 20))

        info_data = [
            ("Tipo", orcamento.tipo or "N/A"),
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
        else:
            if len(selected) == 1:
                messagebox.showinfo("Sucesso", "Orçamento eliminado com sucesso!")
            else:
                messagebox.showinfo("Sucesso", f"{len(selected)} orçamentos eliminados com sucesso!")

        # Reload
        self.carregar_orcamentos()


class OrcamentoDialog(ctk.CTkToplevel):
    """Dialog para criar/editar orçamento"""

    def __init__(self, parent, manager: OrcamentoManager, db_session: Session, orcamento: Optional[Orcamento] = None):
        super().__init__(parent)

        self.manager = manager
        self.db_session = db_session
        self.clientes_manager = ClientesManager(db_session)
        self.orcamento = orcamento
        self.orcamento_criado = False
        self.orcamento_atualizado = False

        # Window config
        self.title("Editar Orçamento" if orcamento else "Novo Orçamento")
        self.geometry("800x750")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f"800x750+{x}+{y}")

        # Create widgets
        self.create_widgets()

        # Load data if editing
        if self.orcamento:
            self.load_data()

    def create_widgets(self):
        """Create dialog widgets"""

        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="✏️ Editar Orçamento" if self.orcamento else "➕ Novo Orçamento",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 20))

        # Scrollable form
        scroll = ctk.CTkScrollableFrame(main_frame)
        scroll.pack(fill="both", expand=True)

        # Código *
        ctk.CTkLabel(scroll, text="Código do Orçamento *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.codigo_entry = ctk.CTkEntry(scroll, placeholder_text="Ex: 20250909_Orçamento-SGS_Conf", height=35)
        self.codigo_entry.pack(fill="x", pady=(0, 10))

        # Tipo e Versão (2 columns)
        tipo_versao_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_versao_frame.pack(fill="x", pady=(10, 10))

        # Tipo *
        tipo_col = ctk.CTkFrame(tipo_versao_frame, fg_color="transparent")
        tipo_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(tipo_col, text="Tipo *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.tipo_combo = ctk.CTkComboBox(
            tipo_col,
            values=["frontend", "backend"],
            height=35,
            command=self.on_tipo_change
        )
        self.tipo_combo.set("frontend")
        self.tipo_combo.pack(fill="x")

        # Versão (only for frontend)
        versao_col = ctk.CTkFrame(tipo_versao_frame, fg_color="transparent")
        versao_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(versao_col, text="Versão (Frontend)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.versao_entry = ctk.CTkEntry(versao_col, placeholder_text="Ex: V1, V2", height=35)
        self.versao_entry.pack(fill="x")

        # Cliente
        ctk.CTkLabel(scroll, text="Cliente", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))

        # Load clientes
        clientes = self.clientes_manager.listar_todos()
        cliente_names = ["(Nenhum)"] + [f"{c.numero} - {c.nome}" for c in clientes]
        self.clientes_map = {f"{c.numero} - {c.nome}": c.id for c in clientes}

        self.cliente_combo = ctk.CTkComboBox(
            scroll,
            values=cliente_names,
            height=35
        )
        self.cliente_combo.set("(Nenhum)")
        self.cliente_combo.pack(fill="x", pady=(0, 10))

        # Data de Criação e Data do Evento (2 columns)
        datas_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        datas_frame.pack(fill="x", pady=(10, 10))

        # Data de Criação *
        data_criacao_col = ctk.CTkFrame(datas_frame, fg_color="transparent")
        data_criacao_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(data_criacao_col, text="Data de Criação *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.data_criacao_entry = ctk.CTkEntry(
            data_criacao_col,
            placeholder_text="YYYY-MM-DD",
            height=35
        )
        self.data_criacao_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.data_criacao_entry.pack(fill="x")

        # Data do Evento
        data_evento_col = ctk.CTkFrame(datas_frame, fg_color="transparent")
        data_evento_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(data_evento_col, text="Data do Evento", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.data_evento_entry = ctk.CTkEntry(
            data_evento_col,
            placeholder_text="Ex: 2025-05-29 | 2025-07-06",
            height=35
        )
        self.data_evento_entry.pack(fill="x")

        # Local do Evento
        ctk.CTkLabel(scroll, text="Local do Evento", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.local_evento_entry = ctk.CTkEntry(scroll, placeholder_text="Ex: Lisboa, Porto", height=35)
        self.local_evento_entry.pack(fill="x", pady=(0, 10))

        # Descrição da Proposta
        ctk.CTkLabel(scroll, text="Descrição da Proposta", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.descricao_textbox = ctk.CTkTextbox(scroll, height=80)
        self.descricao_textbox.pack(fill="x", pady=(0, 10))

        # Status
        ctk.CTkLabel(scroll, text="Status", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.status_combo = ctk.CTkComboBox(
            scroll,
            values=["rascunho", "enviado", "aprovado", "rejeitado"],
            height=35
        )
        self.status_combo.set("rascunho")
        self.status_combo.pack(fill="x", pady=(0, 10))

        # Notas Contratuais
        ctk.CTkLabel(scroll, text="Notas Contratuais", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.notas_textbox = ctk.CTkTextbox(scroll, height=80)
        self.notas_textbox.pack(fill="x", pady=(0, 10))

        # Info text
        info_label = ctk.CTkLabel(
            scroll,
            text="ℹ️ Após criar o orçamento, você poderá adicionar secções e items.",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(pady=(10, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            width=120,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar",
            command=self.save,
            width=120,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        save_btn.pack(side="left")

    def on_tipo_change(self, value):
        """Handle tipo change"""
        if value == "backend":
            # Clear versao for backend
            self.versao_entry.delete(0, "end")
            self.versao_entry.configure(state="disabled", placeholder_text="N/A (Backend)")
        else:
            self.versao_entry.configure(state="normal", placeholder_text="Ex: V1, V2")

    def load_data(self):
        """Load orcamento data into form"""
        if not self.orcamento:
            return

        # Basic fields
        self.codigo_entry.insert(0, self.orcamento.codigo or "")
        self.tipo_combo.set(self.orcamento.tipo or "frontend")

        if self.orcamento.versao:
            self.versao_entry.delete(0, "end")
            self.versao_entry.insert(0, self.orcamento.versao)

        # Trigger tipo change to enable/disable versao
        self.on_tipo_change(self.orcamento.tipo or "frontend")

        # Cliente
        if self.orcamento.cliente:
            cliente_value = f"{self.orcamento.cliente.numero} - {self.orcamento.cliente.nome}"
            self.cliente_combo.set(cliente_value)

        # Dates
        if self.orcamento.data_criacao:
            self.data_criacao_entry.delete(0, "end")
            self.data_criacao_entry.insert(0, self.orcamento.data_criacao.strftime("%Y-%m-%d"))

        if self.orcamento.data_evento:
            self.data_evento_entry.insert(0, self.orcamento.data_evento)

        if self.orcamento.local_evento:
            self.local_evento_entry.insert(0, self.orcamento.local_evento)

        # Text fields
        if self.orcamento.descricao_proposta:
            self.descricao_textbox.insert("1.0", self.orcamento.descricao_proposta)

        if self.orcamento.status:
            self.status_combo.set(self.orcamento.status)

        if self.orcamento.notas_contratuais:
            self.notas_textbox.insert("1.0", self.orcamento.notas_contratuais)

    def save(self):
        """Save orcamento"""
        # Validate required fields
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showerror("Erro", "O código do orçamento é obrigatório!")
            return

        tipo = self.tipo_combo.get()

        data_criacao_str = self.data_criacao_entry.get().strip()
        if not data_criacao_str:
            messagebox.showerror("Erro", "A data de criação é obrigatória!")
            return

        # Parse data_criacao
        try:
            data_criacao = datetime.strptime(data_criacao_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Erro", "Data de criação inválida! Use o formato YYYY-MM-DD")
            return

        # Get versao (only for frontend)
        versao = None
        if tipo == "frontend":
            versao = self.versao_entry.get().strip() or None

        # Get cliente_id
        cliente_id = None
        cliente_value = self.cliente_combo.get()
        if cliente_value != "(Nenhum)":
            cliente_id = self.clientes_map.get(cliente_value)

        # Prepare data
        data = {
            "codigo": codigo,
            "tipo": tipo,
            "versao": versao,
            "cliente_id": cliente_id,
            "data_criacao": data_criacao,
            "data_evento": self.data_evento_entry.get().strip() or None,
            "local_evento": self.local_evento_entry.get().strip() or None,
            "descricao_proposta": self.descricao_textbox.get("1.0", "end-1c").strip() or None,
            "status": self.status_combo.get(),
            "notas_contratuais": self.notas_textbox.get("1.0", "end-1c").strip() or None,
        }

        # Create or update
        try:
            if self.orcamento:
                # Update
                sucesso, _, erro = self.manager.atualizar_orcamento(self.orcamento.id, **data)
                if sucesso:
                    self.orcamento_atualizado = True
                    messagebox.showinfo("Sucesso", "Orçamento atualizado com sucesso!")
                    self.destroy()
                else:
                    messagebox.showerror("Erro", f"Erro ao atualizar orçamento: {erro}")
            else:
                # Create
                sucesso, _, erro = self.manager.criar_orcamento(**data)
                if sucesso:
                    self.orcamento_criado = True
                    messagebox.showinfo("Sucesso", "Orçamento criado com sucesso!")
                    self.destroy()
                else:
                    messagebox.showerror("Erro", f"Erro ao criar orçamento: {erro}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

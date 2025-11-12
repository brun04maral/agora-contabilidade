# -*- coding: utf-8 -*-
"""
Tela de Orçamentos - Gestão de orçamentos (Cliente e Empresa)
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from logic.clientes import ClientesManager
from ui.components.data_table_v2 import DataTableV2
from typing import Optional
from datetime import date, datetime
from tkinter import messagebox
from database.models.orcamento import Orcamento, PropostaSecao, PropostaItem
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
            {"key": "versao_cliente", "label": "PDF Cliente", "width": 100},
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
            versao_cliente = "✓" if orc.tem_versao_cliente else "-"

            data.append({
                "id": orc.id,
                "codigo": orc.codigo or "",
                "cliente": cliente_nome,
                "data_criacao": data_str,
                "valor_total": valor_str,
                "status": orc.status or "rascunho",
                "versao_cliente": versao_cliente,
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
            self.table.clear_selection()

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

        # Clear selection after closing dialog (whether updated or cancelled)
        self.table.clear_selection()

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
            text=f"📋 {orcamento.codigo}",
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
        # Janela maior para incluir gestão de itens
        window_width = 1100
        window_height = 850
        self.geometry(f"{window_width}x{window_height}")
        self.resizable(True, True)
        self.minsize(900, 700)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.winfo_screenheight() // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

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

        # Código * (automático)
        ctk.CTkLabel(scroll, text="Código do Orçamento (Automático)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.codigo_entry = ctk.CTkEntry(
            scroll,
            placeholder_text="Gerado automaticamente",
            height=35,
            state="readonly",
            fg_color=("#F0F0F0", "#2b2b2b")
        )
        self.codigo_entry.pack(fill="x", pady=(0, 10))

        # Auto-gerar código se for novo orçamento
        if not self.orcamento:
            proximo_codigo = self.manager.gerar_proximo_codigo()
            self.codigo_entry.configure(state="normal")
            self.codigo_entry.insert(0, proximo_codigo)
            self.codigo_entry.configure(state="readonly")

        # Cliente (com autocomplete)
        ctk.CTkLabel(scroll, text="Cliente", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))

        # Load clientes
        from ui.components.autocomplete_entry import AutocompleteEntry
        clientes = self.clientes_manager.listar_todos()
        cliente_names = [f"{c.numero} - {c.nome}" for c in clientes]
        self.clientes_map = {f"{c.numero} - {c.nome}": c.id for c in clientes}

        self.cliente_autocomplete = AutocompleteEntry(
            scroll,
            options=cliente_names,
            placeholder="Começar a escrever o nome ou número do cliente..."
        )
        self.cliente_autocomplete.pack(fill="x", pady=(0, 10))

        # Data de Criação e Data do Evento (2 columns)
        from ui.components.date_picker import DatePickerEntry
        datas_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        datas_frame.pack(fill="x", pady=(10, 10))

        # Data de Criação *
        data_criacao_col = ctk.CTkFrame(datas_frame, fg_color="transparent")
        data_criacao_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(data_criacao_col, text="Data de Criação *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.data_criacao_picker = DatePickerEntry(
            data_criacao_col,
            default_date=date.today(),
            placeholder="Selecionar data de criação..."
        )
        self.data_criacao_picker.pack(fill="x")

        # Data do Evento (com range picker)
        data_evento_col = ctk.CTkFrame(datas_frame, fg_color="transparent")
        data_evento_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(data_evento_col, text="Data do Evento", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))

        from ui.components.date_range_picker import DateRangePicker
        self.data_evento_picker = DateRangePicker(
            data_evento_col,
            placeholder="Selecionar período do evento..."
        )
        self.data_evento_picker.pack(fill="x")

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

        # Separador
        separator = ctk.CTkFrame(scroll, height=2, fg_color="gray")
        separator.pack(fill="x", pady=(20, 10))

        # Versão Cliente (opcional)
        ctk.CTkLabel(
            scroll,
            text="📄 Versão para Cliente (PDF)",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", pady=(10, 10))

        self.tem_versao_cliente_var = ctk.IntVar(value=0)
        self.tem_versao_cliente_check = ctk.CTkCheckBox(
            scroll,
            text="Gerar versão PDF para cliente (sem campos económicos)",
            variable=self.tem_versao_cliente_var,
            command=self.toggle_versao_cliente_fields
        )
        self.tem_versao_cliente_check.pack(anchor="w", pady=(0, 10))

        # Frame para campos condicionais
        self.versao_cliente_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.versao_cliente_frame.pack(fill="x", pady=(0, 10))

        # Título Cliente
        ctk.CTkLabel(self.versao_cliente_frame, text="Título para Cliente", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.titulo_cliente_entry = ctk.CTkEntry(self.versao_cliente_frame, placeholder_text="Ex: Proposta de Vídeo - Evento SGS", height=35)
        self.titulo_cliente_entry.pack(fill="x", pady=(0, 10))

        # Descrição Cliente
        ctk.CTkLabel(self.versao_cliente_frame, text="Descrição para Cliente", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.descricao_cliente_textbox = ctk.CTkTextbox(self.versao_cliente_frame, height=80)
        self.descricao_cliente_textbox.pack(fill="x", pady=(0, 10))

        # Botão Exportar PDF (apenas quando editando)
        if self.orcamento:
            export_pdf_btn = ctk.CTkButton(
                self.versao_cliente_frame,
                text="📄 Exportar Proposta para PDF",
                command=self.exportar_proposta_pdf,
                height=35,
                fg_color="#2196F3",
                hover_color="#1976D2"
            )
            export_pdf_btn.pack(fill="x", pady=(10, 10))

        # Inicialmente ocultar campos
        self.versao_cliente_frame.pack_forget()

        # Info text (guardar referência para posicionamento do toggle)
        info_text = "ℹ️ Após criar o orçamento, você poderá adicionar secções e items." if not self.orcamento else "ℹ️ Gerir itens do orçamento abaixo:"
        self.info_label = ctk.CTkLabel(
            scroll,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.info_label.pack(pady=(10, 10))

        # Seção de Gestão de Itens (apenas quando editando)
        if self.orcamento:
            self.create_items_section(scroll)
            self.create_proposta_items_section(scroll)

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

    def toggle_versao_cliente_fields(self):
        """Show/hide versao cliente fields based on checkbox"""
        if self.tem_versao_cliente_var.get():
            # Show frame before info_label to maintain correct order
            self.versao_cliente_frame.pack(fill="x", pady=(0, 10), before=self.info_label)

            # Show proposta items section if orcamento exists
            if self.orcamento and hasattr(self, 'proposta_items_main_container'):
                self.proposta_items_main_container.pack(fill="both", expand=True, pady=(0, 10))
                self.carregar_itens_proposta()
        else:
            self.versao_cliente_frame.pack_forget()

            # Hide proposta items section
            if hasattr(self, 'proposta_items_main_container'):
                self.proposta_items_main_container.pack_forget()

    def create_items_section(self, parent):
        """Cria seção para gestão de itens (apenas quando editando)"""

        # Separador
        separator = ctk.CTkFrame(parent, height=2, fg_color="gray")
        separator.pack(fill="x", pady=(15, 15))

        # Header da seção de itens
        items_header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        items_header_frame.pack(fill="x", pady=(0, 10))

        items_title = ctk.CTkLabel(
            items_header_frame,
            text="📦 Itens do Orçamento",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        items_title.pack(side="left")

        # Botões da seção
        items_buttons_frame = ctk.CTkFrame(items_header_frame, fg_color="transparent")
        items_buttons_frame.pack(side="right")

        add_item_btn = ctk.CTkButton(
            items_buttons_frame,
            text="➕ Adicionar Item",
            command=self.adicionar_item,
            width=140,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_item_btn.pack(side="left", padx=(0, 5))

        refresh_btn = ctk.CTkButton(
            items_buttons_frame,
            text="🔄",
            command=self.carregar_itens,
            width=30,
            height=30,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        refresh_btn.pack(side="left")

        # Container scrollável para itens
        self.items_container = ctk.CTkFrame(parent)
        self.items_container.pack(fill="both", expand=True, pady=(0, 10))

        # Carregar itens
        self.carregar_itens()

    def carregar_itens(self):
        """Carrega e renderiza secções e itens do orçamento"""
        if not self.orcamento:
            return

        # Limpar container
        for widget in self.items_container.winfo_children():
            widget.destroy()

        # Obter secções
        secoes = self.manager.obter_secoes(self.orcamento.id)

        if not secoes:
            no_secoes_label = ctk.CTkLabel(
                self.items_container,
                text="⚠️ Nenhuma secção encontrada.",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            no_secoes_label.pack(pady=20)
            return

        # Criar scrollable frame
        items_scroll = ctk.CTkScrollableFrame(self.items_container)
        items_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Renderizar cada secção
        for secao in secoes:
            if secao.parent_id is None:  # Apenas secções principais
                self.render_secao_compacta(items_scroll, secao)

        # Separador antes dos totais
        separator = ctk.CTkFrame(items_scroll, height=2, fg_color="gray")
        separator.pack(fill="x", pady=(15, 10))

        # Frame de totais
        totais_frame = ctk.CTkFrame(items_scroll, fg_color="#1e1e1e")
        totais_frame.pack(fill="x", pady=(0, 10), padx=5)

        totais_title = ctk.CTkLabel(
            totais_frame,
            text="💰 Totais",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        totais_title.pack(pady=(10, 5))

        # Total Parcial 1 (Serviços + Equipamento)
        if self.orcamento.total_parcial_1:
            parcial1_label = ctk.CTkLabel(
                totais_frame,
                text=f"Total Parcial 1 (Serviços + Equipamento): {float(self.orcamento.total_parcial_1):.2f}€",
                font=ctk.CTkFont(size=13),
                text_color="#90CAF9"
            )
            parcial1_label.pack(pady=2)

        # Total Parcial 2 (Despesas)
        if self.orcamento.total_parcial_2:
            parcial2_label = ctk.CTkLabel(
                totais_frame,
                text=f"Total Parcial 2 (Despesas): {float(self.orcamento.total_parcial_2):.2f}€",
                font=ctk.CTkFont(size=13),
                text_color="#90CAF9"
            )
            parcial2_label.pack(pady=2)

        # Separador antes do total geral
        separator_total = ctk.CTkFrame(totais_frame, height=1, fg_color="gray")
        separator_total.pack(fill="x", padx=20, pady=(10, 5))

        # TOTAL GERAL
        total_label = ctk.CTkLabel(
            totais_frame,
            text=f"TOTAL: {float(self.orcamento.valor_total or 0):.2f}€",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        )
        total_label.pack(pady=(5, 15))

    def render_secao_compacta(self, parent, secao, level=0):
        """Renderiza uma secção de forma compacta"""

        # Frame da secção
        secao_frame = ctk.CTkFrame(parent, fg_color="#2b2b2b")
        secao_frame.pack(fill="x", pady=3, padx=(level * 15, 0))

        # Header da secção
        secao_header = ctk.CTkFrame(secao_frame, fg_color="transparent")
        secao_header.pack(fill="x", padx=8, pady=5)

        # Nome da secção
        indent = "  " * level
        icon = "📁" if secao.subsecoes else "📄"
        secao_label = ctk.CTkLabel(
            secao_header,
            text=f"{indent}{icon} {secao.nome}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        secao_label.pack(side="left")

        # Botão adicionar item
        add_btn = ctk.CTkButton(
            secao_header,
            text="+ Item",
            command=lambda s=secao: self.adicionar_item_em_secao(s.id),
            width=65,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_btn.pack(side="right")

        # Itens da secção
        itens = self.manager.obter_itens(self.orcamento.id, secao.id)

        if itens:
            for item in itens:
                self.render_item_compacto(secao_frame, item)
        else:
            no_items_label = ctk.CTkLabel(
                secao_frame,
                text="  (Sem itens)",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            no_items_label.pack(fill="x", padx=20, pady=3)

        # Renderizar subsecções
        for subsecao in secao.subsecoes:
            self.render_secao_compacta(parent, subsecao, level + 1)

    def render_item_compacto(self, parent, item):
        """Renderiza um item de forma compacta"""

        item_frame = ctk.CTkFrame(parent, fg_color="#1e1e1e")
        item_frame.pack(fill="x", padx=8, pady=2)

        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(side="left", fill="x", expand=True, padx=8, pady=5)

        # Descrição
        desc_label = ctk.CTkLabel(
            content_frame,
            text=f"• {item.descricao}",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        desc_label.pack(anchor="w")

        # Detalhes compactos
        detalhes = f"Qtd:{item.quantidade} × {item.dias}d × {float(item.preco_unitario):.2f}€"
        if item.desconto > 0:
            detalhes += f" | -{float(item.desconto)*100:.0f}%"
        detalhes += f" = {float(item.total):.2f}€"

        if item.equipamento:
            detalhes += f" | 🔧{item.equipamento.numero}"

        detalhes_label = ctk.CTkLabel(
            content_frame,
            text=detalhes,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        detalhes_label.pack(anchor="w")

        # Botões de ação
        actions_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=5)

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            command=lambda i=item: self.editar_item(i),
            width=28,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            command=lambda i=item: self.eliminar_item(i),
            width=28,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        delete_btn.pack(side="left", padx=2)

    def adicionar_item(self):
        """Abre dialog para adicionar item"""
        if not self.orcamento:
            return

        dialog = ItemDialog(
            self,
            self.manager,
            self.db_session,
            self.orcamento.id
        )
        self.wait_window(dialog)

        if dialog.item_salvo:
            self.carregar_itens()
            # Recalcular e atualizar campos de valor
            self.manager.recalcular_totais(self.orcamento.id)
            self.orcamento = self.manager.obter_orcamento(self.orcamento.id)

    def adicionar_item_em_secao(self, secao_id):
        """Abre dialog para adicionar item em secção específica"""
        if not self.orcamento:
            return

        dialog = ItemDialog(
            self,
            self.manager,
            self.db_session,
            self.orcamento.id,
            secao_id=secao_id
        )
        self.wait_window(dialog)

        if dialog.item_salvo:
            self.carregar_itens()
            # Recalcular e atualizar campos de valor
            self.manager.recalcular_totais(self.orcamento.id)
            self.orcamento = self.manager.obter_orcamento(self.orcamento.id)

    def editar_item(self, item):
        """Abre dialog para editar item"""
        if not self.orcamento:
            return

        dialog = ItemDialog(
            self,
            self.manager,
            self.db_session,
            self.orcamento.id,
            item=item
        )
        self.wait_window(dialog)

        if dialog.item_salvo:
            self.carregar_itens()
            # Recalcular e atualizar campos de valor
            self.manager.recalcular_totais(self.orcamento.id)
            self.orcamento = self.manager.obter_orcamento(self.orcamento.id)

    def eliminar_item(self, item):
        """Elimina item"""
        from tkinter import messagebox

        if not messagebox.askyesno(
            "Confirmar Eliminação",
            f"Tem a certeza que deseja eliminar o item '{item.descricao}'?"
        ):
            return

        sucesso, erro = self.manager.eliminar_item(item.id)

        if sucesso:
            messagebox.showinfo("Sucesso", "Item eliminado com sucesso!")
            self.carregar_itens()
            # Recalcular e atualizar campos de valor
            self.manager.recalcular_totais(self.orcamento.id)
            self.orcamento = self.manager.obter_orcamento(self.orcamento.id)
        else:
            messagebox.showerror("Erro", f"Erro ao eliminar item: {erro}")

    def create_proposta_items_section(self, parent):
        """Cria seção para gestão de itens da proposta (versão cliente)"""

        # Separador
        separator = ctk.CTkFrame(parent, height=2, fg_color="gray")
        separator.pack(fill="x", pady=(15, 15))

        # Container principal (inicialmente oculto)
        self.proposta_items_main_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.proposta_items_main_container.pack(fill="both", expand=True, pady=(0, 10))
        self.proposta_items_main_container.pack_forget()  # Ocultar inicialmente

        # Header da seção de itens da proposta
        items_header_frame = ctk.CTkFrame(self.proposta_items_main_container, fg_color="transparent")
        items_header_frame.pack(fill="x", pady=(0, 10))

        items_title = ctk.CTkLabel(
            items_header_frame,
            text="📋 Itens da Proposta (Versão Cliente)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        items_title.pack(side="left")

        # Botões da seção
        items_buttons_frame = ctk.CTkFrame(items_header_frame, fg_color="transparent")
        items_buttons_frame.pack(side="right")

        add_item_btn = ctk.CTkButton(
            items_buttons_frame,
            text="➕ Adicionar Item",
            command=self.adicionar_item_proposta,
            width=140,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_item_btn.pack(side="left", padx=(0, 5))

        refresh_btn = ctk.CTkButton(
            items_buttons_frame,
            text="🔄",
            command=self.carregar_itens_proposta,
            width=30,
            height=30,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        refresh_btn.pack(side="left")

        # Container scrollável para itens
        self.proposta_items_container = ctk.CTkFrame(self.proposta_items_main_container)
        self.proposta_items_container.pack(fill="both", expand=True, pady=(0, 10))

        # Carregar itens se houver proposta
        if self.orcamento and self.orcamento.tem_versao_cliente:
            self.carregar_itens_proposta()

    def carregar_itens_proposta(self):
        """Carrega e renderiza itens da proposta"""
        if not self.orcamento:
            return

        # Limpar container
        for widget in self.proposta_items_container.winfo_children():
            widget.destroy()

        # Obter secções da proposta
        proposta_secoes = self.db_session.query(PropostaSecao).filter(
            PropostaSecao.orcamento_id == self.orcamento.id
        ).order_by(PropostaSecao.ordem).all()

        if not proposta_secoes:
            no_items_label = ctk.CTkLabel(
                self.proposta_items_container,
                text="⚠️ Nenhum item de proposta ainda. Clique em '➕ Adicionar Item' para começar.",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            no_items_label.pack(pady=20)
            return

        # Criar scrollable frame
        items_scroll = ctk.CTkScrollableFrame(self.proposta_items_container)
        items_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Renderizar cada secção
        for secao in proposta_secoes:
            # Header da secção
            secao_frame = ctk.CTkFrame(items_scroll, fg_color="#2b2b2b")
            secao_frame.pack(fill="x", pady=(10, 5), padx=5)

            secao_header = ctk.CTkFrame(secao_frame, fg_color="transparent")
            secao_header.pack(fill="x", padx=10, pady=8)

            secao_label = ctk.CTkLabel(
                secao_header,
                text=f"📁 {secao.nome}",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            secao_label.pack(side="left")

            if secao.subtotal:
                subtotal_label = ctk.CTkLabel(
                    secao_header,
                    text=f"{float(secao.subtotal):.2f}€",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#4CAF50"
                )
                subtotal_label.pack(side="right")

            # Items da secção
            itens = self.db_session.query(PropostaItem).filter(
                PropostaItem.secao_id == secao.id
            ).order_by(PropostaItem.ordem).all()

            if itens:
                items_container = ctk.CTkFrame(items_scroll, fg_color="transparent")
                items_container.pack(fill="x", padx=15, pady=(0, 5))

                for item in itens:
                    self.render_item_proposta_compacto(items_container, item)

    def render_item_proposta_compacto(self, parent, item):
        """Renderiza item da proposta de forma compacta"""

        item_frame = ctk.CTkFrame(parent, fg_color="#1e1e1e")
        item_frame.pack(fill="x", padx=8, pady=2)

        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(side="left", fill="x", expand=True, padx=8, pady=5)

        # Descrição
        desc_label = ctk.CTkLabel(
            content_frame,
            text=f"• {item.descricao}",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        desc_label.pack(anchor="w")

        # Detalhes compactos
        detalhes = f"Qtd:{item.quantidade} × {item.dias}d × {float(item.preco_unitario):.2f}€"
        if item.desconto > 0:
            detalhes += f" | -{float(item.desconto)*100:.0f}%"
        detalhes += f" = {float(item.total):.2f}€"

        detalhes_label = ctk.CTkLabel(
            content_frame,
            text=detalhes,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        detalhes_label.pack(anchor="w")

        # Botões de ação
        actions_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=5)

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            command=lambda i=item: self.editar_item_proposta(i),
            width=28,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            command=lambda i=item: self.eliminar_item_proposta(i),
            width=28,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#f44336",
            hover_color="#da190b"
        )
        delete_btn.pack(side="left", padx=2)

    def adicionar_item_proposta(self):
        """Abre diálogo para adicionar item à proposta"""
        from ui.dialogs.proposta_item_dialog import PropostaItemDialog

        dialog = PropostaItemDialog(
            self,
            self.db_session,
            self.orcamento.id
        )
        self.wait_window(dialog)

        # Refresh itens
        self.carregar_itens_proposta()

    def editar_item_proposta(self, item):
        """Abre diálogo para editar item da proposta"""
        from ui.dialogs.proposta_item_dialog import PropostaItemDialog

        dialog = PropostaItemDialog(
            self,
            self.db_session,
            self.orcamento.id,
            item
        )
        self.wait_window(dialog)

        # Refresh itens
        self.carregar_itens_proposta()

    def eliminar_item_proposta(self, item):
        """Elimina item da proposta"""
        from tkinter import messagebox

        if not messagebox.askyesno(
            "Confirmar Eliminação",
            f"Tem a certeza que deseja eliminar o item '{item.descricao}' da proposta?"
        ):
            return

        try:
            self.db_session.delete(item)
            self.db_session.commit()
            messagebox.showinfo("Sucesso", "Item eliminado com sucesso!")
            self.carregar_itens_proposta()

            # Recalcular subtotais das secções
            secoes = self.db_session.query(PropostaSecao).filter(
                PropostaSecao.orcamento_id == self.orcamento.id
            ).all()

            for secao in secoes:
                itens = self.db_session.query(PropostaItem).filter(
                    PropostaItem.secao_id == secao.id
                ).all()
                secao.subtotal = sum(float(item.total) for item in itens)

            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            messagebox.showerror("Erro", f"Erro ao eliminar item: {str(e)}")

    def exportar_proposta_pdf(self):
        """Exporta proposta para PDF"""
        from tkinter import filedialog
        from logic.proposta_exporter import PropostaExporter

        if not self.orcamento:
            messagebox.showerror("Erro", "Nenhum orçamento selecionado.")
            return

        if not self.orcamento.tem_versao_cliente:
            messagebox.showerror("Erro", "Este orçamento não tem versão para cliente.")
            return

        # Verificar se tem itens da proposta
        proposta_secoes = self.db_session.query(PropostaSecao).filter(
            PropostaSecao.orcamento_id == self.orcamento.id
        ).first()

        if not proposta_secoes:
            messagebox.showerror(
                "Erro",
                "Nenhum item de proposta encontrado.\nPor favor, adicione itens antes de exportar."
            )
            return

        # Solicitar nome do arquivo
        default_filename = f"Proposta_{self.orcamento.codigo.replace('/', '-')}_{datetime.now().strftime('%Y%m%d')}.pdf"

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_filename,
            title="Guardar Proposta como PDF"
        )

        if not filename:
            return

        try:
            # Exportar PDF
            exporter = PropostaExporter(self.db)
            exporter.exportar_pdf(self.orcamento.id, filename)

            messagebox.showinfo(
                "Sucesso",
                f"Proposta exportada com sucesso!\n\nFicheiro: {filename}"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar PDF: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_data(self):
        """Load orcamento data into form"""
        if not self.orcamento:
            return

        # Basic fields - código (readonly)
        self.codigo_entry.configure(state="normal")
        self.codigo_entry.insert(0, self.orcamento.codigo or "")
        self.codigo_entry.configure(state="readonly")

        # Cliente
        if self.orcamento.cliente:
            cliente_value = f"{self.orcamento.cliente.numero} - {self.orcamento.cliente.nome}"
            self.cliente_autocomplete.set(cliente_value)

        # Dates
        if self.orcamento.data_criacao:
            self.data_criacao_picker.set_date(self.orcamento.data_criacao)

        if self.orcamento.data_evento:
            # Parse data_evento (suporta múltiplos formatos)
            data_evento_str = self.orcamento.data_evento.strip()

            # Detectar separador (pipe ou traço)
            separator = None
            if ' | ' in data_evento_str:
                separator = ' | '
            elif ' - ' in data_evento_str:
                separator = ' - '

            if separator:
                # Range de datas
                parts = data_evento_str.split(separator)
                try:
                    # Tentar formato DD/MM/YYYY primeiro
                    try:
                        start_date = datetime.strptime(parts[0].strip(), '%d/%m/%Y').date()
                        end_date = datetime.strptime(parts[1].strip(), '%d/%m/%Y').date()
                    except ValueError:
                        # Fallback para formato YYYY-MM-DD
                        start_date = datetime.strptime(parts[0].strip(), '%Y-%m-%d').date()
                        end_date = datetime.strptime(parts[1].strip(), '%Y-%m-%d').date()
                    self.data_evento_picker.set_range(start_date, end_date)
                except ValueError:
                    # Se não conseguir parsear, insere texto diretamente
                    self.data_evento_picker.entry.insert(0, data_evento_str)
            else:
                # Data única
                try:
                    # Tentar formato DD/MM/YYYY primeiro
                    try:
                        single_date = datetime.strptime(data_evento_str, '%d/%m/%Y').date()
                    except ValueError:
                        # Fallback para formato YYYY-MM-DD
                        single_date = datetime.strptime(data_evento_str, '%Y-%m-%d').date()
                    self.data_evento_picker.set_range(single_date)
                except ValueError:
                    # Se não conseguir parsear, insere texto diretamente
                    self.data_evento_picker.entry.insert(0, data_evento_str)

        if self.orcamento.local_evento:
            self.local_evento_entry.insert(0, self.orcamento.local_evento)

        # Text fields
        if self.orcamento.descricao_proposta:
            self.descricao_textbox.insert("1.0", self.orcamento.descricao_proposta)

        if self.orcamento.status:
            self.status_combo.set(self.orcamento.status)

        if self.orcamento.notas_contratuais:
            self.notas_textbox.insert("1.0", self.orcamento.notas_contratuais)

        # Versão Cliente
        if self.orcamento.tem_versao_cliente:
            self.tem_versao_cliente_var.set(1)
            self.toggle_versao_cliente_fields()

            if self.orcamento.titulo_cliente:
                self.titulo_cliente_entry.insert(0, self.orcamento.titulo_cliente)

            if self.orcamento.descricao_cliente:
                self.descricao_cliente_textbox.insert("1.0", self.orcamento.descricao_cliente)

    def save(self):
        """Save orcamento"""
        # Validate required fields
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showerror("Erro", "O código do orçamento é obrigatório!")
            return

        # Get data_criacao from picker
        data_criacao = self.data_criacao_picker.get_date()
        if not data_criacao:
            messagebox.showerror("Erro", "A data de criação é obrigatória!")
            return

        # Get cliente_id
        cliente_id = None
        cliente_value = self.cliente_autocomplete.get().strip()
        if cliente_value:
            cliente_id = self.clientes_map.get(cliente_value)

        # Prepare data
        data = {
            "codigo": codigo,
            "cliente_id": cliente_id,
            "data_criacao": data_criacao,
            "data_evento": self.data_evento_picker.get().strip() or None,
            "local_evento": self.local_evento_entry.get().strip() or None,
            "descricao_proposta": self.descricao_textbox.get("1.0", "end-1c").strip() or None,
            "status": self.status_combo.get(),
            "notas_contratuais": self.notas_textbox.get("1.0", "end-1c").strip() or None,
            "tem_versao_cliente": bool(self.tem_versao_cliente_var.get()),
            "titulo_cliente": self.titulo_cliente_entry.get().strip() or None,
            "descricao_cliente": self.descricao_cliente_textbox.get("1.0", "end-1c").strip() or None,
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


class ItemDialog(ctk.CTkToplevel):
    """Dialog para adicionar/editar item do orçamento"""

    def __init__(
        self,
        parent,
        manager: OrcamentoManager,
        db_session: Session,
        orcamento_id: int,
        secao_id: Optional[int] = None,
        item: Optional = None
    ):
        super().__init__(parent)

        self.manager = manager
        self.db_session = db_session
        from logic.equipamento import EquipamentoManager
        self.equipamento_manager = EquipamentoManager(db_session)

        self.orcamento_id = orcamento_id
        self.secao_id_inicial = secao_id
        self.item = item
        self.item_salvo = False

        # Window config
        self.title("Editar Item" if item else "Novo Item")
        self.geometry("700x800")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"700x800+{x}+{y}")

        # Create widgets
        self.create_widgets()

        # Load data if editing
        if self.item:
            self.load_data()

    def create_widgets(self):
        """Create dialog widgets"""
        from tkinter import messagebox
        from decimal import Decimal

        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="✏️ Editar Item" if self.item else "➕ Novo Item",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 20))

        # Scrollable form
        scroll = ctk.CTkScrollableFrame(main_frame)
        scroll.pack(fill="both", expand=True)

        # Secção *
        ctk.CTkLabel(scroll, text="Secção *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))

        # Carregar secções
        secoes = self.manager.obter_secoes(self.orcamento_id)
        secoes_list = []
        self.secoes_map = {}

        for secao in secoes:
            # Incluir subsecções
            if secao.parent_id is None:
                secoes_list.append(secao.nome)
                self.secoes_map[secao.nome] = secao.id

                # Adicionar subsecções indentadas
                for subsecao in secao.subsecoes:
                    nome_subsecao = f"  → {subsecao.nome}"
                    secoes_list.append(nome_subsecao)
                    self.secoes_map[nome_subsecao] = subsecao.id

        self.secao_combo = ctk.CTkComboBox(
            scroll,
            values=secoes_list if secoes_list else ["(Sem secções)"],
            height=35,
            state="readonly"
        )
        if secoes_list:
            self.secao_combo.set(secoes_list[0])
        self.secao_combo.pack(fill="x", pady=(0, 10))

        # Se secao_id_inicial foi fornecido, selecionar essa secção
        if self.secao_id_inicial:
            for nome, sid in self.secoes_map.items():
                if sid == self.secao_id_inicial:
                    self.secao_combo.set(nome)
                    break

        # Separador
        separator1 = ctk.CTkFrame(scroll, height=2, fg_color="gray")
        separator1.pack(fill="x", pady=(10, 15))

        # Tipo de Item
        ctk.CTkLabel(
            scroll,
            text="🔧 Tipo de Item",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        self.tipo_item_var = ctk.StringVar(value="manual")

        tipo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_frame.pack(fill="x", pady=(0, 10))

        manual_radio = ctk.CTkRadioButton(
            tipo_frame,
            text="Item Manual (Serviço/Despesa)",
            variable=self.tipo_item_var,
            value="manual",
            command=self.toggle_tipo_item
        )
        manual_radio.pack(anchor="w", pady=2)

        equipamento_radio = ctk.CTkRadioButton(
            tipo_frame,
            text="Equipamento (selecionar da lista)",
            variable=self.tipo_item_var,
            value="equipamento",
            command=self.toggle_tipo_item
        )
        equipamento_radio.pack(anchor="w", pady=2)

        # Frame para seleção de equipamento (inicialmente oculto)
        self.equipamento_frame = ctk.CTkFrame(scroll, fg_color="transparent")

        ctk.CTkLabel(
            self.equipamento_frame,
            text="Selecionar Equipamento",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=(10, 5))

        # Carregar equipamentos
        equipamentos = self.equipamento_manager.listar_equipamentos()
        equipamento_names = ["(Nenhum)"] + [
            f"{eq.numero} - {eq.produto}" + (f" ({eq.tipo})" if eq.tipo else "")
            for eq in equipamentos
        ]
        self.equipamentos_map = {
            f"{eq.numero} - {eq.produto}" + (f" ({eq.tipo})" if eq.tipo else ""): eq.id
            for eq in equipamentos
        }
        self.equipamentos_data = {eq.id: eq for eq in equipamentos}

        self.equipamento_combo = ctk.CTkComboBox(
            self.equipamento_frame,
            values=equipamento_names,
            height=35,
            command=self.on_equipamento_selecionado
        )
        self.equipamento_combo.set("(Nenhum)")
        self.equipamento_combo.pack(fill="x", pady=(0, 5))

        info_eq = ctk.CTkLabel(
            self.equipamento_frame,
            text="💡 O preço do equipamento será preenchido automaticamente",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_eq.pack(anchor="w", pady=(0, 10))

        # Descrição *
        ctk.CTkLabel(scroll, text="Descrição *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.descricao_entry = ctk.CTkEntry(scroll, placeholder_text="Ex: Câmara Sony FX6", height=35)
        self.descricao_entry.pack(fill="x", pady=(0, 10))

        # Quantidade e Dias (2 columns)
        qtd_dias_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        qtd_dias_frame.pack(fill="x", pady=(10, 10))

        # Quantidade *
        qtd_col = ctk.CTkFrame(qtd_dias_frame, fg_color="transparent")
        qtd_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(qtd_col, text="Quantidade *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.quantidade_entry = ctk.CTkEntry(qtd_col, placeholder_text="1", height=35)
        self.quantidade_entry.insert(0, "1")
        self.quantidade_entry.pack(fill="x")
        self.quantidade_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Dias *
        dias_col = ctk.CTkFrame(qtd_dias_frame, fg_color="transparent")
        dias_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(dias_col, text="Dias *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.dias_entry = ctk.CTkEntry(dias_col, placeholder_text="1", height=35)
        self.dias_entry.insert(0, "1")
        self.dias_entry.pack(fill="x")
        self.dias_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Preço Unitário e Desconto (2 columns)
        preco_desc_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        preco_desc_frame.pack(fill="x", pady=(10, 10))

        # Preço Unitário *
        preco_col = ctk.CTkFrame(preco_desc_frame, fg_color="transparent")
        preco_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(preco_col, text="Preço Unitário (€) *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.preco_entry = ctk.CTkEntry(preco_col, placeholder_text="0.00", height=35)
        self.preco_entry.insert(0, "0.00")
        self.preco_entry.pack(fill="x")
        self.preco_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Desconto (%)
        desc_col = ctk.CTkFrame(preco_desc_frame, fg_color="transparent")
        desc_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(desc_col, text="Desconto (%)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.desconto_entry = ctk.CTkEntry(desc_col, placeholder_text="0", height=35)
        self.desconto_entry.insert(0, "0")
        self.desconto_entry.pack(fill="x")
        self.desconto_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Total (calculado)
        total_frame = ctk.CTkFrame(scroll)
        total_frame.pack(fill="x", pady=(15, 10))

        ctk.CTkLabel(
            total_frame,
            text="💰 TOTAL",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)

        self.total_label = ctk.CTkLabel(
            total_frame,
            text="0.00€",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        self.total_label.pack(side="right", padx=10, pady=10)

        # Separador
        separator2 = ctk.CTkFrame(scroll, height=2, fg_color="gray")
        separator2.pack(fill="x", pady=(15, 15))

        # Campos Económicos (opcionais)
        ctk.CTkLabel(
            scroll,
            text="📊 Campos Económicos (Opcionais)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        # Afetação
        ctk.CTkLabel(scroll, text="Afetação", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(5, 5))
        self.afetacao_combo = ctk.CTkComboBox(
            scroll,
            values=["(Nenhum)", "BA", "RR", "Agora", "Freelancers", "Despesa"],
            height=35
        )
        self.afetacao_combo.set("(Nenhum)")
        self.afetacao_combo.pack(fill="x", pady=(0, 10))

        # Investimento e Amortização (2 columns)
        inv_amort_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        inv_amort_frame.pack(fill="x", pady=(10, 10))

        # Investimento
        inv_col = ctk.CTkFrame(inv_amort_frame, fg_color="transparent")
        inv_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(inv_col, text="Investimento (€)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.investimento_entry = ctk.CTkEntry(inv_col, placeholder_text="0.00", height=35)
        self.investimento_entry.pack(fill="x")

        # Amortização
        amort_col = ctk.CTkFrame(inv_amort_frame, fg_color="transparent")
        amort_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(amort_col, text="Amortização (€)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.amortizacao_entry = ctk.CTkEntry(amort_col, placeholder_text="0.00", height=35)
        self.amortizacao_entry.pack(fill="x")

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

    def toggle_tipo_item(self):
        """Show/hide equipamento frame based on tipo"""
        if self.tipo_item_var.get() == "equipamento":
            self.equipamento_frame.pack(fill="x", pady=(0, 10), after=self.equipamento_frame.master.children[list(self.equipamento_frame.master.children.keys())[5]])
        else:
            self.equipamento_frame.pack_forget()

    def on_equipamento_selecionado(self, choice):
        """Auto-preencher campos quando equipamento é selecionado"""
        if choice == "(Nenhum)":
            return

        equipamento_id = self.equipamentos_map.get(choice)
        if not equipamento_id:
            return

        equipamento = self.equipamentos_data.get(equipamento_id)
        if not equipamento:
            return

        # Auto-preencher descrição
        self.descricao_entry.delete(0, "end")
        self.descricao_entry.insert(0, equipamento.produto or "")

        # Auto-preencher preço de aluguer
        if equipamento.preco_aluguer:
            self.preco_entry.delete(0, "end")
            self.preco_entry.insert(0, f"{float(equipamento.preco_aluguer):.2f}")

        # Calcular total
        self.calcular_total()

    def calcular_total(self):
        """Calcula o total do item baseado em qtd * dias * preço * (1 - desconto)"""
        from decimal import Decimal, InvalidOperation

        try:
            quantidade = Decimal(self.quantidade_entry.get() or "1")
            dias = Decimal(self.dias_entry.get() or "1")
            preco = Decimal(self.preco_entry.get() or "0")
            desconto_pct = Decimal(self.desconto_entry.get() or "0")

            # Converter desconto de % para decimal (10% = 0.1)
            desconto = desconto_pct / 100

            # Calcular total
            total = (quantidade * dias * preco) * (1 - desconto)

            # Atualizar label
            self.total_label.configure(text=f"{float(total):.2f}€")

        except (InvalidOperation, ValueError):
            self.total_label.configure(text="0.00€")

    def load_data(self):
        """Load item data into form"""
        if not self.item:
            return

        # Secção
        for nome, sid in self.secoes_map.items():
            if sid == self.item.secao_id:
                self.secao_combo.set(nome)
                break

        # Se tem equipamento, selecionar tipo equipamento
        if self.item.equipamento_id:
            self.tipo_item_var.set("equipamento")
            self.toggle_tipo_item()

            # Selecionar equipamento
            for nome, eid in self.equipamentos_map.items():
                if eid == self.item.equipamento_id:
                    self.equipamento_combo.set(nome)
                    break

        # Descrição
        if self.item.descricao:
            self.descricao_entry.insert(0, self.item.descricao)

        # Quantidade e dias
        self.quantidade_entry.delete(0, "end")
        self.quantidade_entry.insert(0, str(self.item.quantidade or 1))

        self.dias_entry.delete(0, "end")
        self.dias_entry.insert(0, str(self.item.dias or 1))

        # Preço
        self.preco_entry.delete(0, "end")
        self.preco_entry.insert(0, f"{float(self.item.preco_unitario or 0):.2f}")

        # Desconto (converter de 0.1 para 10%)
        desconto_pct = float(self.item.desconto or 0) * 100
        self.desconto_entry.delete(0, "end")
        self.desconto_entry.insert(0, f"{desconto_pct:.0f}")

        # Campos económicos
        if self.item.afetacao:
            self.afetacao_combo.set(self.item.afetacao)

        if self.item.investimento:
            self.investimento_entry.insert(0, f"{float(self.item.investimento):.2f}")

        if self.item.amortizacao:
            self.amortizacao_entry.insert(0, f"{float(self.item.amortizacao):.2f}")

        # Calcular total
        self.calcular_total()

    def save(self):
        """Save item"""
        from tkinter import messagebox
        from decimal import Decimal

        # Validate
        descricao = self.descricao_entry.get().strip()
        if not descricao:
            messagebox.showerror("Erro", "A descrição é obrigatória!")
            return

        secao_nome = self.secao_combo.get()
        secao_id = self.secoes_map.get(secao_nome)
        if not secao_id:
            messagebox.showerror("Erro", "Selecione uma secção válida!")
            return

        try:
            quantidade = int(self.quantidade_entry.get() or "1")
            dias = int(self.dias_entry.get() or "1")
            preco_unitario = Decimal(self.preco_entry.get() or "0")
            desconto_pct = Decimal(self.desconto_entry.get() or "0")

            # Converter desconto de % para decimal
            desconto = desconto_pct / 100

        except (ValueError, Exception) as e:
            messagebox.showerror("Erro", f"Valores numéricos inválidos: {str(e)}")
            return

        # Get equipamento_id se selecionado
        equipamento_id = None
        if self.tipo_item_var.get() == "equipamento":
            eq_choice = self.equipamento_combo.get()
            if eq_choice != "(Nenhum)":
                equipamento_id = self.equipamentos_map.get(eq_choice)

        # Campos económicos
        afetacao = self.afetacao_combo.get()
        if afetacao == "(Nenhum)":
            afetacao = None

        investimento = None
        amortizacao = None
        try:
            inv_val = self.investimento_entry.get().strip()
            if inv_val:
                investimento = Decimal(inv_val)

            amort_val = self.amortizacao_entry.get().strip()
            if amort_val:
                amortizacao = Decimal(amort_val)
        except:
            pass

        # Prepare data
        data = {
            "secao_id": secao_id,
            "descricao": descricao,
            "quantidade": quantidade,
            "dias": dias,
            "preco_unitario": preco_unitario,
            "desconto": desconto,
            "equipamento_id": equipamento_id,
            "afetacao": afetacao,
            "investimento": investimento,
            "amortizacao": amortizacao,
        }

        # Create or update
        try:
            if self.item:
                # Update
                sucesso, _, erro = self.manager.atualizar_item(self.item.id, **data)
                if sucesso:
                    self.item_salvo = True
                    messagebox.showinfo("Sucesso", "Item atualizado com sucesso!")
                    self.destroy()
                else:
                    messagebox.showerror("Erro", f"Erro ao atualizar item: {erro}")
            else:
                # Create
                sucesso, _, erro = self.manager.adicionar_item(
                    orcamento_id=self.orcamento_id,
                    **data
                )
                if sucesso:
                    self.item_salvo = True
                    messagebox.showinfo("Sucesso", "Item adicionado com sucesso!")
                    self.destroy()
                else:
                    messagebox.showerror("Erro", f"Erro ao adicionar item: {erro}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")


class GerirItensDialog(ctk.CTkToplevel):
    """Dialog para gerir itens do orçamento (adicionar, editar, eliminar)"""

    def __init__(self, parent, manager: OrcamentoManager, db_session: Session, orcamento_id: int):
        super().__init__(parent)

        self.manager = manager
        self.db_session = db_session
        self.orcamento_id = orcamento_id
        self.orcamento = self.manager.obter_orcamento(orcamento_id)

        if not self.orcamento:
            from tkinter import messagebox
            messagebox.showerror("Erro", "Orçamento não encontrado!")
            self.destroy()
            return

        # Window config
        self.title(f"Gerir Itens - {self.orcamento.codigo}")
        self.geometry("1200x800")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"1200x800+{x}+{y}")

        # Create widgets
        self.create_widgets()

        # Load data
        self.carregar_secoes_e_itens()

    def create_widgets(self):
        """Create dialog widgets"""

        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        title = ctk.CTkLabel(
            header_frame,
            text=f"📋 Gerir Itens: {self.orcamento.codigo}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(side="left")

        # Buttons no header
        btn_header_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_header_frame.pack(side="right")

        recalc_btn = ctk.CTkButton(
            btn_header_frame,
            text="🔄 Recalcular Totais",
            command=self.recalcular_totais,
            width=150,
            height=32,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        recalc_btn.pack(side="left", padx=(0, 10))

        close_btn = ctk.CTkButton(
            btn_header_frame,
            text="✓ Fechar",
            command=self.destroy,
            width=100,
            height=32
        )
        close_btn.pack(side="left")

        # Info orçamento
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 15))

        if self.orcamento.cliente:
            cliente_label = ctk.CTkLabel(
                info_frame,
                text=f"Cliente: {self.orcamento.cliente.nome}",
                font=ctk.CTkFont(size=13)
            )
            cliente_label.pack(side="left", padx=10, pady=8)

        status_label = ctk.CTkLabel(
            info_frame,
            text=f"Status: {self.orcamento.status}",
            font=ctk.CTkFont(size=13)
        )
        status_label.pack(side="left", padx=10, pady=8)

        # Totais
        self.totais_frame = ctk.CTkFrame(info_frame)
        self.totais_frame.pack(side="right", padx=10, pady=8)

        self.total_label = ctk.CTkLabel(
            self.totais_frame,
            text=f"Total: {float(self.orcamento.valor_total or 0):.2f}€",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4CAF50"
        )
        self.total_label.pack(side="left", padx=10)

        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame)
        self.scroll_frame.pack(fill="both", expand=True)

        # Bottom buttons
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(10, 0))

        add_item_btn = ctk.CTkButton(
            bottom_frame,
            text="➕ Adicionar Item",
            command=self.adicionar_item,
            width=150,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_item_btn.pack(side="left")

    def carregar_secoes_e_itens(self):
        """Carrega secções e itens do orçamento"""

        # Limpar scroll_frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obter secções
        secoes = self.manager.obter_secoes(self.orcamento_id)

        if not secoes:
            no_secoes_label = ctk.CTkLabel(
                self.scroll_frame,
                text="⚠️ Nenhuma secção encontrada. As secções padrão devem ter sido criadas automaticamente.",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            no_secoes_label.pack(pady=50)
            return

        # Mostrar cada secção
        for secao in secoes:
            if secao.parent_id is None:  # Apenas secções principais
                self.render_secao(secao)

    def render_secao(self, secao, level=0):
        """Renderiza uma secção e suas subsecções"""

        # Frame da secção
        secao_frame = ctk.CTkFrame(self.scroll_frame)
        secao_frame.pack(fill="x", pady=5, padx=(level * 20, 0))

        # Header da secção
        secao_header = ctk.CTkFrame(secao_frame, fg_color="#2b2b2b")
        secao_header.pack(fill="x", padx=2, pady=2)

        # Nome da secção
        indent = "  " * level
        icon = "📁" if secao.subsecoes else "📄"
        secao_title = ctk.CTkLabel(
            secao_header,
            text=f"{indent}{icon} {secao.nome}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        secao_title.pack(side="left", padx=10, pady=8)

        # Botão adicionar item
        add_btn = ctk.CTkButton(
            secao_header,
            text="+ Item",
            command=lambda s=secao: self.adicionar_item_em_secao(s.id),
            width=80,
            height=28,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_btn.pack(side="right", padx=10, pady=5)

        # Items da secção
        itens = self.manager.obter_itens(self.orcamento_id, secao.id)

        if itens:
            # Container de itens
            itens_container = ctk.CTkFrame(secao_frame, fg_color="transparent")
            itens_container.pack(fill="x", padx=10, pady=5)

            for item in itens:
                self.render_item(itens_container, item)
        else:
            # Mensagem de sem itens
            no_items_label = ctk.CTkLabel(
                secao_frame,
                text="  (Sem itens)",
                font=ctk.CTkFont(size=12),
                text_color="gray",
                anchor="w"
            )
            no_items_label.pack(fill="x", padx=20, pady=5)

        # Renderizar subsecções
        for subsecao in secao.subsecoes:
            self.render_secao(subsecao, level + 1)

    def render_item(self, container, item):
        """Renderiza um item"""

        # Frame do item
        item_frame = ctk.CTkFrame(container)
        item_frame.pack(fill="x", pady=2)

        # Conteúdo do item
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        # Descrição e detalhes
        desc_text = f"• {item.descricao}"
        desc_label = ctk.CTkLabel(
            content_frame,
            text=desc_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        desc_label.pack(anchor="w")

        # Detalhes do item
        detalhes = f"  Qtd: {item.quantidade} × {item.dias} dias × {float(item.preco_unitario):.2f}€"

        if item.desconto > 0:
            desconto_pct = float(item.desconto) * 100
            detalhes += f" | Desconto: {desconto_pct:.0f}%"

        detalhes += f" = {float(item.total):.2f}€"

        # Adicionar info de equipamento se houver
        if item.equipamento:
            detalhes += f" | 🔧 {item.equipamento.numero}"

        detalhes_label = ctk.CTkLabel(
            content_frame,
            text=detalhes,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        detalhes_label.pack(anchor="w")

        # Botões de ação
        actions_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=10)

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            command=lambda i=item: self.editar_item(i),
            width=40,
            height=28,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            command=lambda i=item: self.eliminar_item(i),
            width=40,
            height=28,
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        delete_btn.pack(side="left", padx=2)

    def adicionar_item(self):
        """Abre dialog para adicionar item"""
        dialog = ItemDialog(
            self,
            self.manager,
            self.db_session,
            self.orcamento_id
        )
        self.wait_window(dialog)

        if dialog.item_salvo:
            self.carregar_secoes_e_itens()
            self.atualizar_totais()

    def adicionar_item_em_secao(self, secao_id):
        """Abre dialog para adicionar item em secção específica"""
        dialog = ItemDialog(
            self,
            self.manager,
            self.db_session,
            self.orcamento_id,
            secao_id=secao_id
        )
        self.wait_window(dialog)

        if dialog.item_salvo:
            self.carregar_secoes_e_itens()
            self.atualizar_totais()

    def editar_item(self, item):
        """Abre dialog para editar item"""
        dialog = ItemDialog(
            self,
            self.manager,
            self.db_session,
            self.orcamento_id,
            item=item
        )
        self.wait_window(dialog)

        if dialog.item_salvo:
            self.carregar_secoes_e_itens()
            self.atualizar_totais()

    def eliminar_item(self, item):
        """Elimina item"""
        from tkinter import messagebox

        if not messagebox.askyesno(
            "Confirmar Eliminação",
            f"Tem a certeza que deseja eliminar o item '{item.descricao}'?"
        ):
            return

        sucesso, erro = self.manager.eliminar_item(item.id)

        if sucesso:
            messagebox.showinfo("Sucesso", "Item eliminado com sucesso!")
            self.carregar_secoes_e_itens()
            self.atualizar_totais()
        else:
            messagebox.showerror("Erro", f"Erro ao eliminar item: {erro}")

    def recalcular_totais(self):
        """Recalcula totais do orçamento"""
        sucesso, erro = self.manager.recalcular_totais(self.orcamento_id)

        if sucesso:
            from tkinter import messagebox
            messagebox.showinfo("Sucesso", "Totais recalculados com sucesso!")
            self.atualizar_totais()
        else:
            from tkinter import messagebox
            messagebox.showerror("Erro", f"Erro ao recalcular totais: {erro}")

    def atualizar_totais(self):
        """Atualiza display de totais"""
        # Recarregar orçamento
        self.orcamento = self.manager.obter_orcamento(self.orcamento_id)

        # Atualizar label
        self.total_label.configure(
            text=f"Total: {float(self.orcamento.valor_total or 0):.2f}€"
        )

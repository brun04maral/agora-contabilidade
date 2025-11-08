# -*- coding: utf-8 -*-
"""
Tela de Equipamento - Gestão de equipamento da Agora Media
"""
import customtkinter as ctk
from typing import Optional
from sqlalchemy.orm import Session
from logic.equipamento import EquipamentoManager
from ui.components.data_table_v2 import DataTableV2
from database.models.equipamento import Equipamento
from tkinter import messagebox


class EquipamentoScreen(ctk.CTkFrame):
    """
    Tela de gestão de Equipamento
    """

    def __init__(self, parent, db_session: Session, **kwargs):
        """
        Initialize equipamento screen

        Args:
            parent: Parent widget
            db_session: SQLAlchemy database session
        """
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.manager = EquipamentoManager(db_session)

        # Configure
        self.configure(fg_color="transparent")

        # Create widgets
        self.create_widgets()

        # Load data
        self.carregar_equipamentos()

    def create_widgets(self):
        """Create screen widgets"""

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="💻 Equipamento",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(side="left")

        # Buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right")

        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Atualizar",
            command=self.carregar_equipamentos,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(
            button_frame,
            text="➕ Novo Equipamento",
            command=self.adicionar_equipamento,
            width=160,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#2196F3", "#1565C0"),
            hover_color=("#1976D2", "#0D47A1")
        )
        add_btn.pack(side="left")

        # Filters
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Search box
        ctk.CTkLabel(
            filter_frame,
            text="Pesquisar:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Produto, ID ou Descrição...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=(0, 20))
        self.search_entry.bind("<KeyRelease>", lambda e: self.carregar_equipamentos())

        # Tipo filter
        ctk.CTkLabel(
            filter_frame,
            text="Tipo:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.tipo_var = ctk.StringVar(value="Todos")
        self.tipo_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.tipo_var,
            values=self.manager.obter_tipos(),
            command=lambda x: self.carregar_equipamentos(),
            width=150,
            height=35
        )
        self.tipo_dropdown.pack(side="left", padx=(0, 20))

        # Com aluguer checkbox
        self.aluguer_var = ctk.BooleanVar(value=False)
        aluguer_check = ctk.CTkCheckBox(
            filter_frame,
            text="Apenas com preço de aluguer",
            variable=self.aluguer_var,
            command=self.carregar_equipamentos,
            font=ctk.CTkFont(size=13)
        )
        aluguer_check.pack(side="left", padx=(0, 10))

        # Table container
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # DataTable
        self.table = DataTableV2(
            table_container,
            columns=[
                {"key": "numero", "label": "ID", "width": 100},
                {"key": "produto", "label": "Produto", "width": 250},
                {"key": "tipo", "label": "Tipo", "width": 120},
                {"key": "valor_compra", "label": "Valor Compra", "width": 130},
                {"key": "preco_aluguer", "label": "Preço Aluguer/dia", "width": 150},
                {"key": "quantidade", "label": "Qtd", "width": 80},
                {"key": "estado", "label": "Estado", "width": 120},
                {"key": "fornecedor", "label": "Fornecedor", "width": 150},
            ],
            height=500
        )
        self.table.pack(fill="both", expand=True)

        # Action buttons
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(10, 30))

        self.edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Editar",
            command=self.editar_equipamento,
            width=120,
            height=35,
            state="disabled"
        )
        self.edit_btn.pack(side="left", padx=(0, 10))

        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Eliminar",
            command=self.eliminar_equipamento,
            width=120,
            height=35,
            state="disabled",
            fg_color=("#D32F2F", "#B71C1C"),
            hover_color=("#C62828", "#A31515")
        )
        self.delete_btn.pack(side="left")

        # Info label
        self.info_label = ctk.CTkLabel(
            action_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.pack(side="right", padx=20)

        # Selection callback
        self.table.set_selection_callback(self.on_selection_changed)

    def carregar_equipamentos(self):
        """Carrega equipamentos com filtros aplicados"""
        # Get filters
        pesquisa = self.search_entry.get().strip() or None
        filtro_tipo = self.tipo_var.get() if self.tipo_var.get() != "Todos" else None
        filtro_com_aluguer = self.aluguer_var.get()

        # Query
        equipamentos = self.manager.listar_equipamentos(
            filtro_tipo=filtro_tipo,
            filtro_com_aluguer=filtro_com_aluguer,
            pesquisa=pesquisa
        )

        # Format data
        data = []
        for eq in equipamentos:
            data.append({
                "id": eq.id,
                "numero": eq.numero,
                "produto": eq.produto or "-",
                "tipo": eq.tipo or "-",
                "valor_compra": f"€{float(eq.valor_compra or 0):,.2f}",
                "preco_aluguer": f"€{float(eq.preco_aluguer or 0):,.2f}" if eq.preco_aluguer else "-",
                "quantidade": str(eq.quantidade or 1),
                "estado": eq.estado or "-",
                "fornecedor": eq.fornecedor or "-",
            })

        # Update table
        self.table.set_data(data)

        # Update info
        stats = self.manager.estatisticas()
        self.info_label.configure(
            text=f"Total: {len(equipamentos)} equipamentos | "
                 f"Investimento total: €{stats['valor_total_investido']:,.2f} | "
                 f"Com aluguer: {stats['com_preco_aluguer']}"
        )

    def on_selection_changed(self, selected_ids):
        """Handle selection change"""
        has_selection = len(selected_ids) > 0
        single_selection = len(selected_ids) == 1

        self.edit_btn.configure(state="normal" if single_selection else "disabled")
        self.delete_btn.configure(state="normal" if has_selection else "disabled")

    def adicionar_equipamento(self):
        """Abre formulário para adicionar equipamento"""
        dialog = EquipamentoDialog(
            self,
            self.manager,
            title="Novo Equipamento"
        )
        self.wait_window(dialog)

        if dialog.result:
            self.carregar_equipamentos()

    def editar_equipamento(self):
        """Edita equipamento selecionado"""
        selected = self.table.get_selected_rows()
        if len(selected) != 1:
            return

        equipamento_id = selected[0]["id"]
        equipamento = self.manager.obter_equipamento(equipamento_id)

        if not equipamento:
            messagebox.showerror("Erro", "Equipamento não encontrado")
            return

        dialog = EquipamentoDialog(
            self,
            self.manager,
            equipamento=equipamento,
            title="Editar Equipamento"
        )
        self.wait_window(dialog)

        if dialog.result:
            self.carregar_equipamentos()

    def eliminar_equipamento(self):
        """Elimina equipamentos selecionados"""
        selected = self.table.get_selected_rows()
        if not selected:
            return

        # Confirm
        response = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja eliminar {len(selected)} equipamento(s)?\n\n"
            "Esta ação não pode ser desfeita."
        )

        if not response:
            return

        # Delete
        erros = 0
        for row in selected:
            sucesso, erro = self.manager.eliminar_equipamento(row["id"])
            if not sucesso:
                erros += 1

        if erros > 0:
            messagebox.showwarning(
                "Aviso",
                f"{len(selected) - erros} equipamento(s) eliminado(s)\n"
                f"{erros} erro(s)"
            )
        else:
            messagebox.showinfo("Sucesso", f"{len(selected)} equipamento(s) eliminado(s)")

        self.carregar_equipamentos()


class EquipamentoDialog(ctk.CTkToplevel):
    """Dialog para criar/editar equipamento"""

    def __init__(self, parent, manager: EquipamentoManager, equipamento: Optional[Equipamento] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.manager = manager
        self.equipamento = equipamento
        self.result = False

        # Window config
        self.title(kwargs.get("title", "Equipamento"))
        self.geometry("600x700")
        self.resizable(False, False)

        # Center window
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        # Load data if editing
        if self.equipamento:
            self.load_data()

    def create_widgets(self):
        """Create dialog widgets"""

        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Scroll
        scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # Número (auto-generated or display)
        if not self.equipamento:
            proximo = self.manager.proximo_numero()
            ctk.CTkLabel(
                scroll,
                text=f"ID: {proximo}",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", pady=(0, 15))
            self.numero_value = proximo
        else:
            ctk.CTkLabel(
                scroll,
                text=f"ID: {self.equipamento.numero}",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", pady=(0, 15))
            self.numero_value = self.equipamento.numero

        # Produto *
        ctk.CTkLabel(scroll, text="Produto *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.produto_entry = ctk.CTkEntry(scroll, height=35)
        self.produto_entry.pack(fill="x", pady=(0, 10))

        # Tipo
        ctk.CTkLabel(scroll, text="Tipo", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.tipo_entry = ctk.CTkEntry(scroll, placeholder_text="Ex: Vídeo, Áudio, Iluminação", height=35)
        self.tipo_entry.pack(fill="x", pady=(0, 10))

        # Descrição
        ctk.CTkLabel(scroll, text="Descrição", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.descricao_entry = ctk.CTkTextbox(scroll, height=60)
        self.descricao_entry.pack(fill="x", pady=(0, 10))

        # Valores (2 columns)
        valores_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        valores_frame.pack(fill="x", pady=(10, 10))

        # Valor compra
        left_frame = ctk.CTkFrame(valores_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(left_frame, text="Valor Compra (€)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.valor_compra_entry = ctk.CTkEntry(left_frame, placeholder_text="0.00", height=35)
        self.valor_compra_entry.pack(fill="x")

        # Preço aluguer
        right_frame = ctk.CTkFrame(valores_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(right_frame, text="Preço Aluguer/dia (€)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.preco_aluguer_entry = ctk.CTkEntry(right_frame, placeholder_text="0.00", height=35)
        self.preco_aluguer_entry.pack(fill="x")

        # Quantidade e Estado (2 columns)
        detalhes_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        detalhes_frame.pack(fill="x", pady=(10, 10))

        # Quantidade
        qtd_frame = ctk.CTkFrame(detalhes_frame, fg_color="transparent")
        qtd_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(qtd_frame, text="Quantidade", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.quantidade_entry = ctk.CTkEntry(qtd_frame, placeholder_text="1", height=35)
        self.quantidade_entry.pack(fill="x")

        # Estado
        estado_frame = ctk.CTkFrame(detalhes_frame, fg_color="transparent")
        estado_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(estado_frame, text="Estado", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.estado_entry = ctk.CTkEntry(estado_frame, placeholder_text="Novo, Usado, etc", height=35)
        self.estado_entry.pack(fill="x")

        # Fornecedor
        ctk.CTkLabel(scroll, text="Fornecedor", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.fornecedor_entry = ctk.CTkEntry(scroll, height=35)
        self.fornecedor_entry.pack(fill="x", pady=(0, 10))

        # Nota
        ctk.CTkLabel(scroll, text="Nota", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.nota_entry = ctk.CTkTextbox(scroll, height=60)
        self.nota_entry.pack(fill="x", pady=(0, 10))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.destroy,
            width=120,
            height=35
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=self.save,
            width=120,
            height=35,
            fg_color=("#2196F3", "#1565C0"),
            hover_color=("#1976D2", "#0D47A1")
        )
        save_btn.pack(side="right")

    def load_data(self):
        """Load equipamento data into form"""
        if not self.equipamento:
            return

        self.produto_entry.insert(0, self.equipamento.produto or "")
        self.tipo_entry.insert(0, self.equipamento.tipo or "")

        if self.equipamento.descricao:
            self.descricao_entry.insert("1.0", self.equipamento.descricao)

        self.valor_compra_entry.insert(0, str(float(self.equipamento.valor_compra or 0)))
        self.preco_aluguer_entry.insert(0, str(float(self.equipamento.preco_aluguer or 0)))
        self.quantidade_entry.insert(0, str(self.equipamento.quantidade or 1))
        self.estado_entry.insert(0, self.equipamento.estado or "")
        self.fornecedor_entry.insert(0, self.equipamento.fornecedor or "")

        if self.equipamento.nota:
            self.nota_entry.insert("1.0", self.equipamento.nota)

    def save(self):
        """Save equipamento"""
        # Validate
        produto = self.produto_entry.get().strip()
        if not produto:
            messagebox.showerror("Erro", "Produto é obrigatório")
            return

        # Parse valores
        try:
            valor_compra = float(self.valor_compra_entry.get().strip() or 0)
            preco_aluguer = float(self.preco_aluguer_entry.get().strip() or 0)
            quantidade = int(self.quantidade_entry.get().strip() or 1)
        except ValueError:
            messagebox.showerror("Erro", "Valores numéricos inválidos")
            return

        # Prepare data
        data = {
            "produto": produto,
            "tipo": self.tipo_entry.get().strip() or None,
            "descricao": self.descricao_entry.get("1.0", "end-1c").strip() or None,
            "valor_compra": valor_compra,
            "preco_aluguer": preco_aluguer,
            "quantidade": quantidade,
            "estado": self.estado_entry.get().strip() or None,
            "fornecedor": self.fornecedor_entry.get().strip() or None,
            "nota": self.nota_entry.get("1.0", "end-1c").strip() or None,
        }

        # Save
        if self.equipamento:
            # Update
            sucesso, _, erro = self.manager.atualizar_equipamento(self.equipamento.id, **data)
        else:
            # Create
            sucesso, _, erro = self.manager.criar_equipamento(numero=self.numero_value, **data)

        if sucesso:
            self.result = True
            messagebox.showinfo("Sucesso", "Equipamento guardado com sucesso")
            self.destroy()
        else:
            messagebox.showerror("Erro", f"Erro ao guardar: {erro}")

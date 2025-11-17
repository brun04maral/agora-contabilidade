# -*- coding: utf-8 -*-
"""
OutroDialog - Dialog para criar/editar despesas tipo OUTRO (LADO CLIENTE)
"""
import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from decimal import Decimal
from typing import Optional


class OutroDialog(ctk.CTkToplevel):
    """
    Dialog para adicionar/editar despesa tipo OUTRO no LADO CLIENTE

    Campos:
    - Descrição (obrigatório, sem default)
    - Valor Fixo (decimal, obrigatório)
    - Total (readonly, igual ao valor_fixo para consistência visual)
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        secao_id: int,
        item_id: Optional[int] = None
    ):
        super().__init__(parent)

        self.db_session = db_session
        self.manager = OrcamentoManager(db_session)
        self.orcamento_id = orcamento_id
        self.secao_id = secao_id
        self.item_id = item_id
        self.success = False

        # Configurar janela
        self.title("Adicionar Outra Despesa" if not item_id else "Editar Outra Despesa")
        self.geometry("500x470")
        self.resizable(False, False)

        # Modal
        self.transient(parent)
        self.grab_set()

        # Criar widgets
        self.create_widgets()

        # Se edição, carregar dados
        if item_id:
            self.carregar_dados()

        # Calcular total inicial
        self.atualizar_total()

    def create_widgets(self):
        """Cria widgets do dialog"""
        # Container principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Despesa: Outro (Valor Fixo)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Descrição
        ctk.CTkLabel(
            main_frame,
            text="Descrição:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.descricao_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Ex: Despesas administrativas, licenças, etc.",
            height=35
        )
        self.descricao_entry.pack(fill="x", pady=(0, 15))

        # Valor Fixo
        ctk.CTkLabel(
            main_frame,
            text="Valor Fixo (€):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.valor_fixo_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Ex: 150.00",
            height=35
        )
        self.valor_fixo_entry.pack(fill="x", pady=(0, 15))
        self.valor_fixo_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        # Total (readonly, igual ao valor_fixo)
        ctk.CTkLabel(
            main_frame,
            text="Total:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.total_label = ctk.CTkLabel(
            main_frame,
            text="€0.00",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=("#e8f5e0", "#2b4a2b"),
            corner_radius=6,
            padx=15,
            pady=10,
            anchor="w"
        )
        self.total_label.pack(fill="x", pady=(0, 20))

        # Botões
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            width=120,
            fg_color="gray",
            hover_color="#5a5a5a"
        )
        btn_cancelar.pack(side="left", padx=(0, 10))

        btn_gravar = ctk.CTkButton(
            btn_frame,
            text="Gravar",
            command=self.gravar,
            width=120,
            fg_color="#FF9800",
            hover_color="#e68900"
        )
        btn_gravar.pack(side="right")

    def atualizar_total(self):
        """Atualiza total (igual ao valor_fixo) em tempo real"""
        try:
            valor_fixo_str = self.valor_fixo_entry.get().strip()

            if valor_fixo_str:
                valor_fixo = Decimal(valor_fixo_str.replace(',', '.'))
                self.total_label.configure(text=f"€{float(valor_fixo):.2f}")
            else:
                self.total_label.configure(text="€0.00")
        except (ValueError, Exception):
            self.total_label.configure(text="€0.00")

    def carregar_dados(self):
        """Carrega dados do item para edição"""
        from database.models.orcamento import OrcamentoItem

        item = self.db_session.query(OrcamentoItem).filter(
            OrcamentoItem.id == self.item_id
        ).first()

        if not item:
            messagebox.showerror("Erro", "Item não encontrado!")
            self.destroy()
            return

        # Preencher campos
        if item.descricao:
            self.descricao_entry.delete(0, "end")
            self.descricao_entry.insert(0, item.descricao)

        if item.valor_fixo:
            self.valor_fixo_entry.delete(0, "end")
            self.valor_fixo_entry.insert(0, str(float(item.valor_fixo)))

        # Atualizar total
        self.atualizar_total()

    def gravar(self):
        """Grava a outra despesa"""
        try:
            # Validar descrição
            descricao = self.descricao_entry.get().strip()
            if not descricao:
                messagebox.showwarning("Aviso", "Descrição é obrigatória!")
                return

            # Validar valor fixo
            valor_fixo_str = self.valor_fixo_entry.get().strip()
            if not valor_fixo_str:
                messagebox.showwarning("Aviso", "Valor fixo é obrigatório!")
                return

            # Converter valor
            try:
                valor_fixo = Decimal(valor_fixo_str.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Erro", "Valor numérico inválido!")
                return

            # Validar valor positivo
            if valor_fixo <= 0:
                messagebox.showwarning("Aviso", "Valor fixo deve ser maior que 0!")
                return

            # Gravar no banco
            if self.item_id:
                # Editar existente
                sucesso, item, erro = self.manager.atualizar_item_v2(
                    item_id=self.item_id,
                    descricao=descricao,
                    valor_fixo=valor_fixo
                )
                if sucesso:
                    self.item_created_id = self.item_id
            else:
                # Criar novo
                sucesso, item, erro = self.manager.adicionar_item_v2(
                    orcamento_id=self.orcamento_id,
                    secao_id=self.secao_id,
                    tipo='outro',
                    descricao=descricao,
                    valor_fixo=valor_fixo
                )
                if sucesso:
                    self.item_created_id = item.id

            if sucesso:
                self.success = True
                messagebox.showinfo("Sucesso", "Despesa gravada com sucesso!")
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro ao gravar: {erro}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

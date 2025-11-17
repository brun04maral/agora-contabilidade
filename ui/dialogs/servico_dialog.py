# -*- coding: utf-8 -*-
"""
ServicoDialog - Dialog para criar/editar serviços tipo SERVICO (LADO CLIENTE)
"""
import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from decimal import Decimal
from typing import Optional


class ServicoDialog(ctk.CTkToplevel):
    """
    Dialog para adicionar/editar serviço tipo SERVICO no LADO CLIENTE

    Campos:
    - Descrição (obrigatório)
    - Quantidade (inteiro, default 1)
    - Dias (inteiro, default 1)
    - Preço Unitário (decimal, obrigatório)
    - Desconto (decimal 0-100%, default 0)
    - Total (readonly, auto-calculado)

    Cálculo:
    subtotal = quantidade × dias × preço_unitário
    desconto_valor = subtotal × (desconto / 100)
    total = subtotal - desconto_valor
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
        self.title("Adicionar Serviço" if not item_id else "Editar Serviço")
        self.geometry("500x650")
        self.resizable(False, False)

        # Modal
        self.transient(parent)
        self.grab_set()

        # Criar widgets
        self.create_widgets()

        # Se edição, carregar dados
        if item_id:
            self.carregar_dados()
        else:
            # Valores default para novo item
            self.quantidade_entry.insert(0, "1")
            self.dias_entry.insert(0, "1")
            self.desconto_entry.insert(0, "0")

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
            text="Serviço Manual",
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
            placeholder_text="Ex: Desenvolvimento de funcionalidade X",
            height=35
        )
        self.descricao_entry.pack(fill="x", pady=(0, 15))

        # Grid para Quantidade e Dias (lado a lado)
        grid_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 15))
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # Quantidade
        quantidade_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
        quantidade_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkLabel(
            quantidade_frame,
            text="Quantidade:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.quantidade_entry = ctk.CTkEntry(
            quantidade_frame,
            placeholder_text="Ex: 1",
            height=35
        )
        self.quantidade_entry.pack(fill="x")
        self.quantidade_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        # Dias
        dias_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
        dias_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        ctk.CTkLabel(
            dias_frame,
            text="Dias:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.dias_entry = ctk.CTkEntry(
            dias_frame,
            placeholder_text="Ex: 1",
            height=35
        )
        self.dias_entry.pack(fill="x")
        self.dias_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        # Preço Unitário
        ctk.CTkLabel(
            main_frame,
            text="Preço Unitário (€):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.preco_unitario_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Ex: 250.00",
            height=35
        )
        self.preco_unitario_entry.pack(fill="x", pady=(0, 15))
        self.preco_unitario_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        # Desconto
        ctk.CTkLabel(
            main_frame,
            text="Desconto (%):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.desconto_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Ex: 10 (para 10%)",
            height=35
        )
        self.desconto_entry.pack(fill="x", pady=(0, 15))
        self.desconto_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        # Total (readonly)
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
        """
        Atualiza total calculado em tempo real
        Fórmula: total = (quantidade × dias × preço_unitário) - desconto%
        """
        try:
            quantidade_str = self.quantidade_entry.get().strip()
            dias_str = self.dias_entry.get().strip()
            preco_unitario_str = self.preco_unitario_entry.get().strip()
            desconto_str = self.desconto_entry.get().strip() or "0"

            if quantidade_str and dias_str and preco_unitario_str:
                quantidade = int(quantidade_str)
                dias = int(dias_str)
                preco_unitario = Decimal(preco_unitario_str.replace(',', '.'))
                desconto = Decimal(desconto_str.replace(',', '.'))

                # Calcular subtotal
                subtotal = quantidade * dias * preco_unitario

                # Calcular desconto
                desconto_valor = subtotal * (desconto / Decimal('100'))

                # Calcular total
                total = subtotal - desconto_valor

                self.total_label.configure(text=f"€{float(total):.2f}")
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

        if item.quantidade:
            self.quantidade_entry.delete(0, "end")
            self.quantidade_entry.insert(0, str(item.quantidade))

        if item.dias:
            self.dias_entry.delete(0, "end")
            self.dias_entry.insert(0, str(item.dias))

        if item.preco_unitario:
            self.preco_unitario_entry.delete(0, "end")
            self.preco_unitario_entry.insert(0, str(float(item.preco_unitario)))

        if item.desconto:
            self.desconto_entry.delete(0, "end")
            # Converter de decimal (0.10) para percentagem (10)
            desconto_pct = float(item.desconto) * 100
            self.desconto_entry.insert(0, str(desconto_pct))
        else:
            self.desconto_entry.insert(0, "0")

        # Atualizar total
        self.atualizar_total()

    def gravar(self):
        """Grava o serviço"""
        try:
            # Validar descrição
            descricao = self.descricao_entry.get().strip()
            if not descricao:
                messagebox.showwarning("Aviso", "Descrição é obrigatória!")
                return

            # Validar quantidade
            quantidade_str = self.quantidade_entry.get().strip()
            if not quantidade_str:
                messagebox.showwarning("Aviso", "Quantidade é obrigatória!")
                return

            # Validar dias
            dias_str = self.dias_entry.get().strip()
            if not dias_str:
                messagebox.showwarning("Aviso", "Dias é obrigatório!")
                return

            # Validar preço unitário
            preco_unitario_str = self.preco_unitario_entry.get().strip()
            if not preco_unitario_str:
                messagebox.showwarning("Aviso", "Preço unitário é obrigatório!")
                return

            # Validar desconto (opcional, default 0)
            desconto_str = self.desconto_entry.get().strip() or "0"

            # Converter valores
            try:
                quantidade = int(quantidade_str)
                dias = int(dias_str)
                preco_unitario = Decimal(preco_unitario_str.replace(',', '.'))
                desconto_pct = Decimal(desconto_str.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Erro", "Valores numéricos inválidos!")
                return

            # Validar valores positivos
            if quantidade <= 0:
                messagebox.showwarning("Aviso", "Quantidade deve ser maior que 0!")
                return

            if dias <= 0:
                messagebox.showwarning("Aviso", "Dias deve ser maior que 0!")
                return

            if preco_unitario <= 0:
                messagebox.showwarning("Aviso", "Preço unitário deve ser maior que 0!")
                return

            if desconto_pct < 0 or desconto_pct > 100:
                messagebox.showwarning("Aviso", "Desconto deve estar entre 0 e 100%!")
                return

            # Converter desconto de percentagem para decimal (10% -> 0.10)
            desconto_decimal = desconto_pct / Decimal('100')

            # Gravar no banco
            if self.item_id:
                # Editar existente
                sucesso, item, erro = self.manager.atualizar_item_v2(
                    item_id=self.item_id,
                    descricao=descricao,
                    quantidade=quantidade,
                    dias=dias,
                    preco_unitario=preco_unitario,
                    desconto=desconto_decimal
                )
                if sucesso:
                    self.item_created_id = self.item_id
            else:
                # Criar novo
                sucesso, item, erro = self.manager.adicionar_item_v2(
                    orcamento_id=self.orcamento_id,
                    secao_id=self.secao_id,
                    tipo='servico',
                    descricao=descricao,
                    quantidade=quantidade,
                    dias=dias,
                    preco_unitario=preco_unitario,
                    desconto=desconto_decimal
                )
                if sucesso:
                    self.item_created_id = item.id

            if sucesso:
                self.success = True
                messagebox.showinfo("Sucesso", "Serviço gravado com sucesso!")
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro ao gravar: {erro}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

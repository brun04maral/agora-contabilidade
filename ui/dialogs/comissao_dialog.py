# -*- coding: utf-8 -*-
"""
ComissaoDialog - Dialog para criar/editar comissões EMPRESA (LADO EMPRESA)
"""
import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from database.models.orcamento import OrcamentoReparticao
from decimal import Decimal
from typing import Optional


class ComissaoDialog(ctk.CTkToplevel):
    """
    Dialog para adicionar/editar comissão no LADO EMPRESA

    Campos:
    - Beneficiário (dropdown obrigatório: BA, RR, AGORA)
    - Descrição (obrigatório)
    - Percentagem (decimal 0-100, 3 casas decimais, obrigatório)
    - Base de Cálculo (readonly, display only)
    - Total Calculado (readonly, auto-calculado)

    Cálculo:
    total = base_calculo × (percentagem / 100)
    Suporta 3 casas decimais (ex: 5.125%)
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        base_calculo: Decimal,
        item_id: Optional[int] = None
    ):
        super().__init__(parent)

        self.db_session = db_session
        self.manager = OrcamentoManager(db_session)
        self.orcamento_id = orcamento_id
        self.base_calculo = base_calculo  # Base para cálculo da comissão
        self.item_id = item_id
        self.success = False

        # Configurar janela
        self.title("Adicionar Comissão" if not item_id else "Editar Comissão")
        self.geometry("500x520")
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
            text="Comissão - LADO EMPRESA",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # Beneficiário (OBRIGATÓRIO)
        ctk.CTkLabel(
            main_frame,
            text="Beneficiário: *",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f44336"
        ).pack(anchor="w", pady=(0, 5))

        self.beneficiario_var = ctk.StringVar(value="")
        self.beneficiario_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=self.beneficiario_var,
            values=["BA", "RR", "AGORA"],
            height=35
        )
        self.beneficiario_dropdown.pack(fill="x", pady=(0, 15))

        # Descrição
        ctk.CTkLabel(
            main_frame,
            text="Descrição:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.descricao_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Ex: Comissão de Venda",
            height=35
        )
        self.descricao_entry.pack(fill="x", pady=(0, 15))

        # Percentagem (3 casas decimais)
        ctk.CTkLabel(
            main_frame,
            text="Percentagem (%):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.percentagem_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Ex: 5.125 (suporta 3 decimais)",
            height=35
        )
        self.percentagem_entry.pack(fill="x", pady=(0, 15))
        self.percentagem_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        # Base de cálculo (display only)
        ctk.CTkLabel(
            main_frame,
            text="Base de Cálculo:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.base_label = ctk.CTkLabel(
            main_frame,
            text=f"€{float(self.base_calculo):.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#e3f2fd", "#1e3a5f"),
            corner_radius=6,
            padx=15,
            pady=10,
            anchor="w"
        )
        self.base_label.pack(fill="x", pady=(0, 15))

        # Total Calculado (readonly, auto-calculado)
        ctk.CTkLabel(
            main_frame,
            text="Total Calculado:",
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
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        )
        btn_gravar.pack(side="right")

    def atualizar_total(self):
        """
        Atualiza total calculado em tempo real
        Fórmula: total = base_calculo × (percentagem / 100)
        """
        try:
            percentagem_str = self.percentagem_entry.get().strip()

            if percentagem_str:
                percentagem = Decimal(percentagem_str.replace(',', '.'))
                total = self.base_calculo * (percentagem / Decimal('100'))
                self.total_label.configure(text=f"€{float(total):.2f}")
            else:
                self.total_label.configure(text="€0.00")
        except (ValueError, Exception):
            self.total_label.configure(text="€0.00")

    def carregar_dados(self):
        """Carrega dados do item para edição"""
        item = self.db_session.query(OrcamentoReparticao).filter(
            OrcamentoReparticao.id == self.item_id
        ).first()

        if not item:
            messagebox.showerror("Erro", "Item não encontrado!")
            self.destroy()
            return

        # Preencher campos
        if item.beneficiario:
            self.beneficiario_var.set(item.beneficiario)

        if item.descricao:
            self.descricao_entry.delete(0, "end")
            self.descricao_entry.insert(0, item.descricao)

        if item.percentagem:
            self.percentagem_entry.delete(0, "end")
            # Mostrar com 3 casas decimais se tiver
            self.percentagem_entry.insert(0, str(float(item.percentagem)))

        if item.base_calculo:
            self.base_calculo = item.base_calculo
            self.base_label.configure(text=f"€{float(self.base_calculo):.2f}")

        # Atualizar total
        self.atualizar_total()

    def gravar(self):
        """Grava a comissão"""
        try:
            # Validar beneficiário (OBRIGATÓRIO)
            beneficiario = self.beneficiario_var.get()
            if not beneficiario:
                messagebox.showwarning("Aviso", "Beneficiário é obrigatório!")
                return

            # Validar descrição
            descricao = self.descricao_entry.get().strip()
            if not descricao:
                messagebox.showwarning("Aviso", "Descrição é obrigatória!")
                return

            # Validar percentagem
            percentagem_str = self.percentagem_entry.get().strip()
            if not percentagem_str:
                messagebox.showwarning("Aviso", "Percentagem é obrigatória!")
                return

            # Converter valores
            try:
                percentagem = Decimal(percentagem_str.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Erro", "Percentagem inválida!")
                return

            # Validar valores
            if percentagem <= 0:
                messagebox.showwarning("Aviso", "Percentagem deve ser maior que 0!")
                return

            if percentagem > 100:
                messagebox.showwarning("Aviso", "Percentagem não pode ser maior que 100%!")
                return

            # Gravar no banco
            if self.item_id:
                # Editar existente
                sucesso, item, erro = self.manager.atualizar_reparticao(
                    reparticao_id=self.item_id,
                    tipo='comissao',
                    beneficiario=beneficiario,
                    descricao=descricao,
                    percentagem=percentagem,
                    base_calculo=self.base_calculo
                )
                if sucesso:
                    item.total = item.calcular_total()
                    self.db_session.commit()
            else:
                # Criar novo
                reparticao = OrcamentoReparticao(
                    orcamento_id=self.orcamento_id,
                    tipo='comissao',
                    beneficiario=beneficiario,
                    descricao=descricao,
                    percentagem=percentagem,
                    base_calculo=self.base_calculo,
                    total=Decimal('0')
                )
                reparticao.total = reparticao.calcular_total()
                self.db_session.add(reparticao)
                self.db_session.commit()
                sucesso = True

            if sucesso:
                self.success = True
                messagebox.showinfo("Sucesso", "Comissão gravada com sucesso!")
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro ao gravar: {erro if 'erro' in locals() else 'Desconhecido'}")

        except Exception as e:
            self.db_session.rollback()
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

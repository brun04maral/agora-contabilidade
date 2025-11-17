# -*- coding: utf-8 -*-
"""
OutroEmpresaDialog - Diálogo para adicionar/editar items genéricos EMPRESA em orçamentos
Dialog genérico para o lado EMPRESA para items que não se encaixam nas categorias específicas
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from sqlalchemy.orm import Session
from database.models.orcamento import OrcamentoItem


class OutroEmpresaDialog(ctk.CTkToplevel):
    """
    Diálogo para adicionar ou editar item genérico do lado EMPRESA
    Para casos que não se encaixam nas categorias específicas (serviço, equipamento, etc)
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        secao_id: int,
        item: Optional[OrcamentoItem] = None
    ):
        super().__init__(parent)

        self.db = db_session
        self.orcamento_id = orcamento_id
        self.secao_id = secao_id
        self.item = item
        self.is_edit = item is not None

        # Configurar janela
        self.title("Editar Item EMPRESA" if self.is_edit else "Adicionar Outro Item EMPRESA")
        self.geometry("600x520")
        self.resizable(False, False)

        # Tornar modal
        self.transient(parent)
        self.grab_set()

        # Centrar na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (520 // 2)
        self.geometry(f"600x520+{x}+{y}")

        self.create_widgets()

        # Carregar dados se for edição
        if self.is_edit:
            self.load_data()

    def create_widgets(self):
        """Cria widgets do diálogo"""

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="📝 " + ("Editar Item EMPRESA" if self.is_edit else "Outro Item EMPRESA"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=(0, 10))

        # Info
        info_label = ctk.CTkLabel(
            main_frame,
            text="Para items genéricos que não se encaixam nas categorias específicas",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(pady=(0, 15))

        # Scrollable form
        scroll = ctk.CTkScrollableFrame(main_frame)
        scroll.pack(fill="both", expand=True)

        # Descrição *
        ctk.CTkLabel(scroll, text="Descrição *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        ctk.CTkLabel(
            scroll,
            text="Descreva o item de forma clara e detalhada",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(anchor="w", pady=(0, 5))
        self.descricao_textbox = ctk.CTkTextbox(scroll, height=100)
        self.descricao_textbox.pack(fill="x", pady=(0, 10))

        # Beneficiário *
        ctk.CTkLabel(scroll, text="Beneficiário *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.beneficiario_combo = ctk.CTkComboBox(
            scroll,
            values=["BA", "RR"],
            height=35,
            state="readonly"
        )
        self.beneficiario_combo.set("BA")  # Default
        self.beneficiario_combo.pack(fill="x", pady=(0, 10))

        # Quantidade e Valor Unitário (lado a lado)
        qtd_valor_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        qtd_valor_frame.pack(fill="x", pady=(10, 10))

        # Quantidade
        qtd_col = ctk.CTkFrame(qtd_valor_frame, fg_color="transparent")
        qtd_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(qtd_col, text="Quantidade *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.quantidade_entry = ctk.CTkEntry(qtd_col, placeholder_text="Ex: 1", height=35)
        self.quantidade_entry.pack(fill="x")
        self.quantidade_entry.insert(0, "1")
        self.quantidade_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Valor Unitário
        valor_col = ctk.CTkFrame(qtd_valor_frame, fg_color="transparent")
        valor_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(valor_col, text="Valor Unitário (€) *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.valor_unitario_entry = ctk.CTkEntry(valor_col, placeholder_text="Ex: 100.00", height=35)
        self.valor_unitario_entry.pack(fill="x")
        self.valor_unitario_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Total (readonly, calculado)
        ctk.CTkLabel(scroll, text="Total (Calculado)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.total_entry = ctk.CTkEntry(
            scroll,
            placeholder_text="0.00 €",
            height=35,
            state="readonly",
            fg_color=("#F0F0F0", "#2b2b2b")
        )
        self.total_entry.pack(fill="x", pady=(0, 10))

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
        cancel_btn.pack(side="right")

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self.save,
            width=120,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        save_btn.pack(side="right", padx=(0, 10))

    def calcular_total(self):
        """Calcula o total do item"""
        try:
            quantidade = int(self.quantidade_entry.get() or 0)
            valor_unitario = float(self.valor_unitario_entry.get() or 0)

            # Calcular total
            total = quantidade * valor_unitario

            # Atualizar campo total
            self.total_entry.configure(state="normal")
            self.total_entry.delete(0, "end")
            self.total_entry.insert(0, f"{total:.2f} €")
            self.total_entry.configure(state="readonly")
        except ValueError:
            # Se houver erro de conversão, não fazer nada
            pass

    def load_data(self):
        """Carrega dados do item para edição"""
        if not self.item:
            return

        # Preencher campos
        self.descricao_textbox.insert("1.0", self.item.descricao)

        # Beneficiário (afetacao)
        if self.item.afetacao:
            self.beneficiario_combo.set(self.item.afetacao)

        self.quantidade_entry.delete(0, "end")
        self.quantidade_entry.insert(0, str(self.item.quantidade))

        self.valor_unitario_entry.delete(0, "end")
        self.valor_unitario_entry.insert(0, str(float(self.item.preco_unitario)))

        # Calcular total
        self.calcular_total()

    def save(self):
        """Guarda item genérico EMPRESA"""
        # Validação
        descricao = self.descricao_textbox.get("1.0", "end").strip()
        if not descricao:
            messagebox.showerror("Erro", "Por favor, preencha a descrição.")
            return

        beneficiario = self.beneficiario_combo.get()
        if not beneficiario or beneficiario not in ["BA", "RR"]:
            messagebox.showerror("Erro", "Por favor, selecione um beneficiário válido (BA ou RR).")
            return

        try:
            quantidade = int(self.quantidade_entry.get())
            if quantidade <= 0:
                messagebox.showerror("Erro", "Quantidade deve ser maior que 0.")
                return

            valor_unitario = float(self.valor_unitario_entry.get())
            if valor_unitario <= 0:
                messagebox.showerror("Erro", "Valor unitário deve ser maior que 0.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos.")
            return

        # Calcular total
        total = quantidade * valor_unitario

        try:
            if self.is_edit:
                # Atualizar item existente
                self.item.descricao = descricao
                self.item.afetacao = beneficiario
                self.item.quantidade = quantidade
                self.item.dias = 1  # Item genérico não usa dias
                self.item.preco_unitario = valor_unitario
                self.item.desconto = 0  # Sem desconto no lado EMPRESA
                self.item.total = total
            else:
                # Criar novo item
                # Obter próxima ordem
                ultimo_item = self.db.query(OrcamentoItem).filter(
                    OrcamentoItem.secao_id == self.secao_id
                ).order_by(OrcamentoItem.ordem.desc()).first()

                ordem = (ultimo_item.ordem + 1) if ultimo_item else 0

                novo_item = OrcamentoItem(
                    orcamento_id=self.orcamento_id,
                    secao_id=self.secao_id,
                    descricao=descricao,
                    afetacao=beneficiario,
                    quantidade=quantidade,
                    dias=1,  # Item genérico não usa dias
                    preco_unitario=valor_unitario,
                    desconto=0,  # Sem desconto no lado EMPRESA
                    total=total,
                    ordem=ordem
                )
                self.db.add(novo_item)

            self.db.commit()
            messagebox.showinfo("Sucesso", "Item EMPRESA guardado com sucesso!")
            self.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Erro", f"Erro ao guardar item EMPRESA: {str(e)}")

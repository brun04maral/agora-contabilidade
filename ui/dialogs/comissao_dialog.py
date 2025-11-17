# -*- coding: utf-8 -*-
"""
ComissaoDialog - Diálogo para adicionar/editar comissões EMPRESA em orçamentos
Dialog para o lado EMPRESA com cálculo baseado em percentagem sobre base de cálculo
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from sqlalchemy.orm import Session
from database.models.orcamento import OrcamentoItem


class ComissaoDialog(ctk.CTkToplevel):
    """
    Diálogo para adicionar ou editar comissão do lado EMPRESA
    Calcula automaticamente total = base_calculo × (percentagem / 100)
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
        self.title("Editar Comissão EMPRESA" if self.is_edit else "Adicionar Comissão EMPRESA")
        self.geometry("600x550")
        self.resizable(False, False)

        # Tornar modal
        self.transient(parent)
        self.grab_set()

        # Centrar na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f"600x550+{x}+{y}")

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
            text="💰 " + ("Editar Comissão EMPRESA" if self.is_edit else "Nova Comissão EMPRESA"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=(0, 20))

        # Scrollable form
        scroll = ctk.CTkScrollableFrame(main_frame)
        scroll.pack(fill="both", expand=True)

        # Descrição *
        ctk.CTkLabel(scroll, text="Descrição *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.descricao_textbox = ctk.CTkTextbox(scroll, height=80)
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

        # Percentagem e Base de Cálculo (lado a lado)
        calc_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        calc_frame.pack(fill="x", pady=(10, 10))

        # Percentagem
        pct_col = ctk.CTkFrame(calc_frame, fg_color="transparent")
        pct_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(pct_col, text="Percentagem (%) *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.percentagem_entry = ctk.CTkEntry(pct_col, placeholder_text="Ex: 10 ou 7.5", height=35)
        self.percentagem_entry.pack(fill="x")
        self.percentagem_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Base de Cálculo
        base_col = ctk.CTkFrame(calc_frame, fg_color="transparent")
        base_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(base_col, text="Base de Cálculo (€) *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.base_calculo_entry = ctk.CTkEntry(base_col, placeholder_text="Ex: 5000.00", height=35)
        self.base_calculo_entry.pack(fill="x")
        self.base_calculo_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Info de cálculo
        info_label = ctk.CTkLabel(
            scroll,
            text="💡 Total calculado automaticamente: Base de Cálculo × (Percentagem / 100)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(pady=(10, 5))

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

        # Exemplo visual
        exemplo_frame = ctk.CTkFrame(scroll, fg_color=("#E3F2FD", "#1E3A5F"))
        exemplo_frame.pack(fill="x", pady=(10, 10), padx=10)

        exemplo_label = ctk.CTkLabel(
            exemplo_frame,
            text="📝 Exemplo:\n"
                 "Percentagem: 10% | Base: 5000€ → Total: 500€\n"
                 "Percentagem: 7.5% | Base: 2000€ → Total: 150€",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        exemplo_label.pack(pady=10, padx=10)

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
        """Calcula o total da comissão"""
        try:
            percentagem = float(self.percentagem_entry.get() or 0)
            base_calculo = float(self.base_calculo_entry.get() or 0)

            # Calcular total: base × (percentagem / 100)
            total = base_calculo * (percentagem / 100)

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

        # Para edição, precisamos recalcular percentagem a partir do valor unitário
        # Assumindo que preco_unitario armazena a percentagem
        # e quantidade armazena a base de cálculo
        if self.item.quantidade and self.item.preco_unitario:
            # Reconstituir percentagem e base
            base_calculo = float(self.item.quantidade)
            total = float(self.item.total)
            percentagem = (total / base_calculo * 100) if base_calculo > 0 else 0

            self.percentagem_entry.delete(0, "end")
            self.percentagem_entry.insert(0, f"{percentagem:.2f}")

            self.base_calculo_entry.delete(0, "end")
            self.base_calculo_entry.insert(0, f"{base_calculo:.2f}")

        # Calcular total
        self.calcular_total()

    def save(self):
        """Guarda comissão EMPRESA"""
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
            percentagem = float(self.percentagem_entry.get())
            if percentagem <= 0:
                messagebox.showerror("Erro", "Percentagem deve ser maior que 0.")
                return

            base_calculo = float(self.base_calculo_entry.get())
            if base_calculo <= 0:
                messagebox.showerror("Erro", "Base de cálculo deve ser maior que 0.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos.")
            return

        # Calcular total
        total = base_calculo * (percentagem / 100)

        try:
            if self.is_edit:
                # Atualizar item existente
                self.item.descricao = descricao
                self.item.afetacao = beneficiario
                # Armazenar base_calculo em quantidade
                self.item.quantidade = int(base_calculo)
                self.item.dias = 1  # Comissão não usa dias
                # Armazenar percentagem em preco_unitario
                self.item.preco_unitario = percentagem
                self.item.desconto = 0  # Sem desconto
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
                    quantidade=int(base_calculo),  # Armazena base_calculo
                    dias=1,  # Comissão não usa dias
                    preco_unitario=percentagem,  # Armazena percentagem
                    desconto=0,  # Sem desconto
                    total=total,
                    ordem=ordem
                )
                self.db.add(novo_item)

            self.db.commit()
            messagebox.showinfo("Sucesso", "Comissão EMPRESA guardada com sucesso!")
            self.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Erro", f"Erro ao guardar comissão EMPRESA: {str(e)}")

# -*- coding: utf-8 -*-
"""
AluguerEquipamentoDialog - Diálogo para adicionar/editar aluguer de equipamento EMPRESA em orçamentos
Dialog para o lado EMPRESA com cálculo baseado em dias × valor/dia
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from sqlalchemy.orm import Session
from database.models.orcamento import OrcamentoItem
from logic.equipamento import EquipamentoManager


class AluguerEquipamentoDialog(ctk.CTkToplevel):
    """
    Diálogo para adicionar ou editar aluguer de equipamento do lado EMPRESA
    Calcula automaticamente total = dias × valor_dia
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

        # Manager de equipamento
        self.equipamento_manager = EquipamentoManager(db_session)

        # Configurar janela
        self.title("Editar Aluguer Equipamento EMPRESA" if self.is_edit else "Adicionar Aluguer Equipamento EMPRESA")
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
            text="🎬 " + ("Editar Aluguer Equipamento EMPRESA" if self.is_edit else "Novo Aluguer Equipamento EMPRESA"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=(0, 20))

        # Scrollable form
        scroll = ctk.CTkScrollableFrame(main_frame)
        scroll.pack(fill="both", expand=True)

        # Equipamento *
        ctk.CTkLabel(scroll, text="Equipamento *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))

        # Carregar lista de equipamentos
        equipamentos = self.equipamento_manager.listar_equipamentos()

        # Criar mapa id -> nome e lista de nomes
        self.equipamentos_map = {f"{eq.numero} - {eq.produto}": eq.id for eq in equipamentos}
        equipamento_names = list(self.equipamentos_map.keys())

        if not equipamento_names:
            equipamento_names = ["Nenhum equipamento disponível"]

        self.equipamento_combo = ctk.CTkComboBox(
            scroll,
            values=equipamento_names,
            height=35,
            state="readonly" if equipamento_names[0] != "Nenhum equipamento disponível" else "disabled"
        )
        if equipamento_names and equipamento_names[0] != "Nenhum equipamento disponível":
            self.equipamento_combo.set(equipamento_names[0])
        self.equipamento_combo.pack(fill="x", pady=(0, 10))

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

        # Dias e Valor/Dia (lado a lado)
        dias_valor_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        dias_valor_frame.pack(fill="x", pady=(10, 10))

        # Dias
        dias_col = ctk.CTkFrame(dias_valor_frame, fg_color="transparent")
        dias_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(dias_col, text="Dias *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.dias_entry = ctk.CTkEntry(dias_col, placeholder_text="Ex: 3", height=35)
        self.dias_entry.pack(fill="x")
        self.dias_entry.insert(0, "1")
        self.dias_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Valor/Dia
        valor_col = ctk.CTkFrame(dias_valor_frame, fg_color="transparent")
        valor_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(valor_col, text="Valor/Dia (€) *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.valor_dia_entry = ctk.CTkEntry(valor_col, placeholder_text="Ex: 150.00", height=35)
        self.valor_dia_entry.pack(fill="x")
        self.valor_dia_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Info de cálculo
        info_label = ctk.CTkLabel(
            scroll,
            text="💡 Total calculado automaticamente: Dias × Valor/Dia",
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
                 "Equipamento: Canon C70 | Dias: 3 | Valor/Dia: 150€ → Total: 450€\n"
                 "Equipamento: Sony A7 | Dias: 5 | Valor/Dia: 80€ → Total: 400€",
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
        """Calcula o total do aluguer"""
        try:
            dias = int(self.dias_entry.get() or 0)
            valor_dia = float(self.valor_dia_entry.get() or 0)

            # Calcular total: dias × valor_dia
            total = dias * valor_dia

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

        # Selecionar equipamento
        if self.item.equipamento_id:
            equipamento = self.equipamento_manager.obter_equipamento(self.item.equipamento_id)
            if equipamento:
                equipamento_key = f"{equipamento.numero} - {equipamento.produto}"
                if equipamento_key in self.equipamentos_map:
                    self.equipamento_combo.set(equipamento_key)

        # Beneficiário (afetacao)
        if self.item.afetacao:
            self.beneficiario_combo.set(self.item.afetacao)

        # Dias
        self.dias_entry.delete(0, "end")
        self.dias_entry.insert(0, str(self.item.dias))

        # Valor/Dia (preco_unitario)
        self.valor_dia_entry.delete(0, "end")
        self.valor_dia_entry.insert(0, str(float(self.item.preco_unitario)))

        # Calcular total
        self.calcular_total()

    def save(self):
        """Guarda aluguer de equipamento EMPRESA"""
        # Validação
        equipamento_nome = self.equipamento_combo.get()
        if not equipamento_nome or equipamento_nome == "Nenhum equipamento disponível":
            messagebox.showerror("Erro", "Por favor, selecione um equipamento.")
            return

        equipamento_id = self.equipamentos_map.get(equipamento_nome)
        if not equipamento_id:
            messagebox.showerror("Erro", "Equipamento inválido.")
            return

        beneficiario = self.beneficiario_combo.get()
        if not beneficiario or beneficiario not in ["BA", "RR"]:
            messagebox.showerror("Erro", "Por favor, selecione um beneficiário válido (BA ou RR).")
            return

        try:
            dias = int(self.dias_entry.get())
            if dias <= 0:
                messagebox.showerror("Erro", "Dias deve ser maior que 0.")
                return

            valor_dia = float(self.valor_dia_entry.get())
            if valor_dia <= 0:
                messagebox.showerror("Erro", "Valor/Dia deve ser maior que 0.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos.")
            return

        # Calcular total
        total = dias * valor_dia

        # Obter equipamento para descrição
        equipamento = self.equipamento_manager.obter_equipamento(equipamento_id)
        if not equipamento:
            messagebox.showerror("Erro", "Equipamento não encontrado.")
            return

        descricao = f"Aluguer {equipamento.numero} - {equipamento.produto} ({dias} dia{'s' if dias > 1 else ''})"

        try:
            if self.is_edit:
                # Atualizar item existente
                self.item.equipamento_id = equipamento_id
                self.item.descricao = descricao
                self.item.afetacao = beneficiario
                self.item.quantidade = 1  # Aluguer sempre quantidade 1
                self.item.dias = dias
                self.item.preco_unitario = valor_dia
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
                    equipamento_id=equipamento_id,
                    descricao=descricao,
                    afetacao=beneficiario,
                    quantidade=1,  # Aluguer sempre quantidade 1
                    dias=dias,
                    preco_unitario=valor_dia,
                    desconto=0,  # Sem desconto no lado EMPRESA
                    total=total,
                    ordem=ordem
                )
                self.db.add(novo_item)

            self.db.commit()
            messagebox.showinfo("Sucesso", "Aluguer de equipamento EMPRESA guardado com sucesso!")
            self.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Erro", f"Erro ao guardar aluguer de equipamento EMPRESA: {str(e)}")

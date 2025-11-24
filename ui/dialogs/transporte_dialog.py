import customtkinter as ctk
from utils.base_dialogs import BaseDialogMedium
from tkinter import messagebox
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from decimal import Decimal
from typing import Optional

class TransporteDialog(BaseDialogMedium):
    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        secao_id: int,
        item_id: Optional[int] = None
    ):
        super().__init__(parent, title="Adicionar Transporte" if not item_id else "Editar Transporte", width=500, height=450)
        self.db_session = db_session
        self.manager = OrcamentoManager(db_session)
        self.orcamento_id = orcamento_id
        self.secao_id = secao_id
        self.item_id = item_id
        self.success = False

        self.create_widgets()
        if item_id:
            self.carregar_dados()
        self.atualizar_total()

    def create_widgets(self):
        main = self.main_frame

        ctk.CTkLabel(main, text="Despesa: Transporte", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 20))
        ctk.CTkLabel(main, text="Descrição:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.descricao_entry = ctk.CTkEntry(main, placeholder_text="Ex: Van de aluguer", height=35)
        self.descricao_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(main, text="Quantidade (Dias):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.dias_entry = ctk.CTkEntry(main, placeholder_text="Ex: 3", height=35)
        self.dias_entry.pack(fill="x", pady=(0, 15))
        self.dias_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        ctk.CTkLabel(main, text="Valor Diário (€):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.valor_dia_entry = ctk.CTkEntry(main, placeholder_text="Ex: 75.00", height=35)
        self.valor_dia_entry.pack(fill="x", pady=(0, 15))
        self.valor_dia_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        ctk.CTkLabel(main, text="Total:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.total_label = ctk.CTkLabel(main, text="€0.00", font=ctk.CTkFont(size=18, weight="bold"),
                                        fg_color=("#e8f5e0", "#2b4a2b"),
                                        corner_radius=6, padx=15, pady=10, anchor="w")
        self.total_label.pack(fill="x", pady=(0, 20))

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, width=120, fg_color="gray", hover_color="#5a5a5a").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Gravar", command=self.gravar, width=120, fg_color="#FF9800", hover_color="#e68900").pack(side="right")

    def atualizar_total(self):
        try:
            dias_str = self.dias_entry.get().strip()
            valor_dia_str = self.valor_dia_entry.get().strip()
            if dias_str and valor_dia_str:
                dias = int(dias_str)
                valor_dia = Decimal(valor_dia_str.replace(',', '.'))
                total = dias * valor_dia
                self.total_label.configure(text=f"€{float(total):.2f}")
            else:
                self.total_label.configure(text="€0.00")
        except (ValueError, Exception):
            self.total_label.configure(text="€0.00")

    def carregar_dados(self):
        from database.models.orcamento import OrcamentoItem
        item = self.db_session.query(OrcamentoItem).filter(
            OrcamentoItem.id == self.item_id
        ).first()
        if not item:
            messagebox.showerror("Erro", "Item não encontrado!")
            self.destroy()
            return

        if item.descricao:
            self.descricao_entry.delete(0, "end")
            self.descricao_entry.insert(0, item.descricao)
        if item.dias:
            self.dias_entry.delete(0, "end")
            self.dias_entry.insert(0, str(item.dias))
        if item.valor_dia:
            self.valor_dia_entry.delete(0, "end")
            self.valor_dia_entry.insert(0, str(float(item.valor_dia)))

        self.atualizar_total()

    def gravar(self):
        try:
            descricao = self.descricao_entry.get().strip()
            if not descricao:
                messagebox.showwarning("Aviso", "Descrição é obrigatória!")
                return
            dias_str = self.dias_entry.get().strip()
            if not dias_str:
                messagebox.showwarning("Aviso", "Quantidade (Dias) é obrigatória!")
                return
            valor_dia_str = self.valor_dia_entry.get().strip()
            if not valor_dia_str:
                messagebox.showwarning("Aviso", "Valor diário é obrigatório!")
                return
            try:
                dias = int(dias_str)
                valor_dia = Decimal(valor_dia_str.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Erro", "Valores numéricos inválidos!")
                return
            if dias <= 0:
                messagebox.showwarning("Aviso", "Quantidade (Dias) deve ser maior que 0!")
                return
            if valor_dia <= 0:
                messagebox.showwarning("Aviso", "Valor diário deve ser maior que 0!")
                return
            if self.item_id:
                sucesso, item, erro = self.manager.atualizar_item_v2(
                    item_id=self.item_id,
                    descricao=descricao,
                    dias=dias,
                    valor_dia=valor_dia
                )
                if not sucesso:
                    messagebox.showerror("Erro", f"Erro ao gravar: {erro}")
            else:
                sucesso, item, erro = self.manager.adicionar_item_v2(
                    orcamento_id=self.orcamento_id,
                    secao_id=self.secao_id,
                    tipo='transporte',
                    descricao=descricao,
                    dias=dias,
                    valor_dia=valor_dia
                )
                if not sucesso:
                    messagebox.showerror("Erro", f"Erro ao gravar: {erro}")
            if sucesso:
                self.success = True
                self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

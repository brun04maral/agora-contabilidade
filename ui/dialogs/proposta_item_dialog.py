import customtkinter as ctk
from utils.base_dialogs import BaseDialogMedium
from tkinter import messagebox
from typing import Optional
from sqlalchemy.orm import Session
from database.models.orcamento import PropostaSecao, PropostaItem

class PropostaItemDialog(BaseDialogMedium):
    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        item: Optional[PropostaItem] = None
    ):
        super().__init__(parent, title="Novo Item da Proposta" if not item else "Editar Item da Proposta", width=500, height=450)
        self.db = db_session
        self.orcamento_id = orcamento_id
        self.item = item
        self.is_edit = item is not None

        self.create_widgets()
        if self.is_edit:
            self.load_data()

    def create_widgets(self):
        main = self.main_frame

        ctk.CTkLabel(main, text="📋 " + ("Editar Item da Proposta" if self.is_edit else "Novo Item da Proposta"), font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 20))
        ctk.CTkLabel(main, text="Secção *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        secao_frame = ctk.CTkFrame(main, fg_color="transparent")
        secao_frame.pack(fill="x", pady=(0, 10))

        secoes = self.db.query(PropostaSecao).filter(PropostaSecao.orcamento_id == self.orcamento_id).order_by(PropostaSecao.ordem).all()
        secao_names = [s.nome for s in secoes]
        self.secoes_map = {s.nome: s.id for s in secoes}
        self.secao_combo = ctk.CTkComboBox(secao_frame, values=secao_names if secao_names else ["Criar nova secção..."], height=35, state="readonly" if secao_names else "disabled")
        self.secao_combo.pack(side="left", fill="x", expand=True, padx=(0, 5))
        if secao_names:
            self.secao_combo.set(secao_names[0])
        ctk.CTkButton(secao_frame, text="➕ Nova Secção", command=self.criar_nova_secao, width=120, height=35, fg_color="#4CAF50", hover_color="#45a049").pack(side="right")

        ctk.CTkLabel(main, text="Descrição *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.descricao_textbox = ctk.CTkTextbox(main, height=80)
        self.descricao_textbox.pack(fill="x", pady=(0, 10))

        qtd_dias_frame = ctk.CTkFrame(main, fg_color="transparent")
        qtd_dias_frame.pack(fill="x", pady=(10, 10))

        qtd_col = ctk.CTkFrame(qtd_dias_frame, fg_color="transparent")
        qtd_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(qtd_col, text="Quantidade *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.quantidade_entry = ctk.CTkEntry(qtd_col, placeholder_text="Ex: 1", height=35)
        self.quantidade_entry.pack(fill="x")
        self.quantidade_entry.insert(0, "1")
        self.quantidade_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        dias_col = ctk.CTkFrame(qtd_dias_frame, fg_color="transparent")
        dias_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(dias_col, text="Dias *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.dias_entry = ctk.CTkEntry(dias_col, placeholder_text="Ex: 1", height=35)
        self.dias_entry.pack(fill="x")
        self.dias_entry.insert(0, "1")
        self.dias_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        ctk.CTkLabel(main, text="Preço Unitário (€) *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.preco_entry = ctk.CTkEntry(main, placeholder_text="Ex: 100.00", height=35)
        self.preco_entry.pack(fill="x", pady=(0, 10))
        self.preco_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        ctk.CTkLabel(main, text="Desconto (%)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.desconto_entry = ctk.CTkEntry(main, placeholder_text="Ex: 10", height=35)
        self.desconto_entry.pack(fill="x", pady=(0, 10))
        self.desconto_entry.insert(0, "0")
        self.desconto_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        ctk.CTkLabel(main, text="Total (Calculado)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.total_entry = ctk.CTkEntry(main, placeholder_text="0.00 €", height=35, state="readonly", fg_color=("#F0F0F0", "#2b2b2b"))
        self.total_entry.pack(fill="x", pady=(0, 10))

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, width=120, height=35, fg_color="gray", hover_color="darkgray").pack(side="right")
        ctk.CTkButton(btn_frame, text="Guardar", command=self.save, width=120, height=35, fg_color="#4CAF50", hover_color="#45a049").pack(side="right", padx=(0, 10))

    def calcular_total(self):
        try:
            quantidade = int(self.quantidade_entry.get().strip() or "0")
            dias = int(self.dias_entry.get().strip() or "0")
            preco_unitario = float(self.preco_entry.get().strip().replace(',', '.') or "0")
            desconto_pct = float(self.desconto_entry.get().strip().replace(',', '.') or "0")
            subtotal = quantidade * dias * preco_unitario
            desconto_valor = subtotal * (desconto_pct / 100.0)
            total = subtotal - desconto_valor
            self.total_entry.configure(state="normal")
            self.total_entry.delete(0, "end")
            self.total_entry.insert(0, f"{total:.2f} €")
            self.total_entry.configure(state="readonly")
        except Exception:
            self.total_entry.configure(state="normal")
            self.total_entry.delete(0, "end")
            self.total_entry.insert(0, "0.00 €")
            self.total_entry.configure(state="readonly")

    def load_data(self):
        item = self.item
        if not item:
            messagebox.showerror("Erro", "Item não encontrado!")
            self.destroy()
            return

        secao_nome = None
        for nome, secao_id in self.secoes_map.items():
            if secao_id == item.secao_id:
                secao_nome = nome
                break
        if secao_nome:
            self.secao_combo.set(secao_nome)
        self.descricao_textbox.insert("1.0", item.descricao)
        self.quantidade_entry.delete(0, "end")
        self.quantidade_entry.insert(0, str(item.quantidade))
        self.dias_entry.delete(0, "end")
        self.dias_entry.insert(0, str(item.dias))
        self.preco_entry.delete(0, "end")
        self.preco_entry.insert(0, str(float(item.preco_unitario)))
        desconto_pct = float(item.desconto or 0) * 100
        self.desconto_entry.delete(0, "end")
        self.desconto_entry.insert(0, str(desconto_pct))
        self.calcular_total()

    def save(self):
        try:
            secao_nome = self.secao_combo.get()
            secao_id = self.secoes_map.get(secao_nome)
            descricao = self.descricao_textbox.get("1.0", "end").strip()
            quantidade = self.quantidade_entry.get().strip()
            dias = self.dias_entry.get().strip()
            preco = self.preco_entry.get().strip()
            desconto = self.desconto_entry.get().strip() or "0"
            if not secao_id:
                messagebox.showwarning("Aviso", "Secção é obrigatória!")
                return
            if not descricao:
                messagebox.showwarning("Aviso", "Descrição é obrigatória!")
                return
            try:
                quantidade = int(quantidade)
                dias = int(dias)
                preco_unitario = float(preco.replace(',', '.'))
                desconto_pct = float(desconto.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Erro", "Valores numéricos inválidos!")
                return
            if quantidade <= 0 or dias <= 0 or preco_unitario <= 0 or desconto_pct < 0 or desconto_pct > 100:
                messagebox.showwarning("Aviso", "Valores inválidos!")
                return
            desconto_decimal = desconto_pct / 100.0
            if self.is_edit:
                item = self.item
                item.secao_id = secao_id
                item.descricao = descricao
                item.quantidade = quantidade
                item.dias = dias
                item.preco_unitario = preco_unitario
                item.desconto = desconto_decimal
                self.db.commit()
            else:
                novo_item = PropostaItem(
                    orcamento_id=self.orcamento_id,
                    secao_id=secao_id,
                    descricao=descricao,
                    quantidade=quantidade,
                    dias=dias,
                    preco_unitario=preco_unitario,
                    desconto=desconto_decimal
                )
                self.db.add(novo_item)
                self.db.commit()
            self.success = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def criar_nova_secao(self):
        # Implementa aqui popup/modal ou lógica para criar uma secção nova,
        # tipicamente chama outro dialog ou faz um insert rápido.
        pass

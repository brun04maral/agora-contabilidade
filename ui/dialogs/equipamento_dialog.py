import customtkinter as ctk
from utils.base_dialogs import BaseDialogMedium
from tkinter import messagebox
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from logic.equipamento import EquipamentoManager
from decimal import Decimal
from typing import Optional

class EquipamentoDialog(BaseDialogMedium):
    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        secao_id: int,
        item_id: Optional[int] = None
    ):
        super().__init__(parent, title="Adicionar Equipamento" if not item_id else "Editar Equipamento", width=500, height=450)
        self.db_session = db_session
        self.manager = OrcamentoManager(db_session)
        self.equipamento_manager = EquipamentoManager(db_session)
        self.orcamento_id = orcamento_id
        self.secao_id = secao_id
        self.item_id = item_id
        self.success = False

        self.equipamentos_map = {}
        self.equipamento_selecionado_id = None

        self.create_widgets()
        self.carregar_equipamentos()
        if item_id:
            self.carregar_dados()
        else:
            self.quantidade_entry.insert(0, "1")
            self.dias_entry.insert(0, "1")
            self.desconto_entry.insert(0, "0")
        self.atualizar_total()

    def create_widgets(self):
        main = self.main_frame

        ctk.CTkLabel(main, text="Equipamento", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 20))
        ctk.CTkLabel(main, text="Selecionar Equipamento (opcional):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.equipamento_dropdown = ctk.CTkOptionMenu(main, values=["-- Nenhum --"], command=self.ao_selecionar_equipamento, height=35)
        self.equipamento_dropdown.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(main, text="Descrição:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.descricao_entry = ctk.CTkEntry(main, placeholder_text="Ex: Câmara Sony FX3 com objetivas", height=35)
        self.descricao_entry.pack(fill="x", pady=(0, 15))

        grid_frame = ctk.CTkFrame(main, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 15))
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        quantidade_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
        quantidade_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(quantidade_frame, text="Quantidade:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.quantidade_entry = ctk.CTkEntry(quantidade_frame, placeholder_text="Ex: 1", height=35)
        self.quantidade_entry.pack(fill="x")
        self.quantidade_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        dias_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
        dias_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(dias_frame, text="Dias:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.dias_entry = ctk.CTkEntry(dias_frame, placeholder_text="Ex: 1", height=35)
        self.dias_entry.pack(fill="x")
        self.dias_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        ctk.CTkLabel(main, text="Preço Unitário (€/dia):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.preco_unitario_entry = ctk.CTkEntry(main, placeholder_text="Ex: 150.00", height=35)
        self.preco_unitario_entry.pack(fill="x", pady=(0, 15))
        self.preco_unitario_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        ctk.CTkLabel(main, text="Desconto (%):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.desconto_entry = ctk.CTkEntry(main, placeholder_text="Ex: 10 (para 10%)", height=35)
        self.desconto_entry.pack(fill="x", pady=(0, 15))
        self.desconto_entry.bind("<KeyRelease>", lambda e: self.atualizar_total())

        ctk.CTkLabel(main, text="Total:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.total_label = ctk.CTkLabel(main, text="€0.00", font=ctk.CTkFont(size=18, weight="bold"),
                                        fg_color=("#e8f5e0", "#2b4a2b"),
                                        corner_radius=6, padx=15, pady=10, anchor="w")
        self.total_label.pack(fill="x", pady=(0, 20))

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy, width=120, fg_color="gray", hover_color="#5a5a5a").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Gravar", command=self.gravar, width=120, fg_color="#FF9800", hover_color="#e68900").pack(side="right")

    def carregar_equipamentos(self):
        try:
            equipamentos = self.equipamento_manager.listar_equipamentos(filtro_com_aluguer=True)
            if equipamentos:
                self.equipamentos_map = {}
                opcoes = ["-- Nenhum --"]
                for eq in equipamentos:
                    display = f"{eq.numero} - {eq.produto} (€{float(eq.preco_aluguer):.2f}/dia)"
                    self.equipamentos_map[display] = eq
                    opcoes.append(display)
                self.equipamento_dropdown.configure(values=opcoes)
        except Exception as e:
            print(f"Erro ao carregar equipamentos: {e}")

    def ao_selecionar_equipamento(self, escolha: str):
        if escolha == "-- Nenhum --":
            self.equipamento_selecionado_id = None
            return
        equipamento = self.equipamentos_map.get(escolha)
        if equipamento:
            self.equipamento_selecionado_id = equipamento.id
            self.descricao_entry.delete(0, "end")
            descricao = equipamento.produto
            if equipamento.descricao:
                descricao = f"{equipamento.produto} - {equipamento.descricao}"
            self.descricao_entry.insert(0, descricao)
            if equipamento.preco_aluguer:
                self.preco_unitario_entry.delete(0, "end")
                self.preco_unitario_entry.insert(0, str(float(equipamento.preco_aluguer)))
            self.atualizar_total()

    def atualizar_total(self):
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
                subtotal = quantidade * dias * preco_unitario
                desconto_valor = subtotal * (desconto / Decimal('100'))
                total = subtotal - desconto_valor
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
            desconto_pct = float(item.desconto) * 100
            self.desconto_entry.insert(0, str(desconto_pct))
        else:
            self.desconto_entry.insert(0, "0")
        if item.equipamento_id:
            self.equipamento_selecionado_id = item.equipamento_id
            equipamento = self.equipamento_manager.obter_equipamento(item.equipamento_id)
            if equipamento:
                for display, eq in self.equipamentos_map.items():
                    if eq.id == item.equipamento_id:
                        self.equipamento_dropdown.set(display)
                        break
        self.atualizar_total()

    def gravar(self):
        try:
            descricao = self.descricao_entry.get().strip()
            if not descricao:
                messagebox.showwarning("Aviso", "Descrição é obrigatória!")
                return
            quantidade_str = self.quantidade_entry.get().strip()
            if not quantidade_str:
                messagebox.showwarning("Aviso", "Quantidade é obrigatória!")
                return
            dias_str = self.dias_entry.get().strip()
            if not dias_str:
                messagebox.showwarning("Aviso", "Dias é obrigatório!")
                return
            preco_unitario_str = self.preco_unitario_entry.get().strip()
            if not preco_unitario_str:
                messagebox.showwarning("Aviso", "Preço unitário é obrigatório!")
                return
            desconto_str = self.desconto_entry.get().strip() or "0"
            try:
                quantidade = int(quantidade_str)
                dias = int(dias_str)
                preco_unitario = Decimal(preco_unitario_str.replace(',', '.'))
                desconto_pct = Decimal(desconto_str.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Erro", "Valores numéricos inválidos!")
                return
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
            desconto_decimal = desconto_pct / Decimal('100')
            if self.item_id:
                sucesso, item, erro = self.manager.atualizar_item_v2(
                    item_id=self.item_id,
                    descricao=descricao,
                    quantidade=quantidade,
                    dias=dias,
                    preco_unitario=preco_unitario,
                    desconto=desconto_decimal,
                    equipamento_id=self.equipamento_selecionado_id
                )
                if not sucesso:
                    messagebox.showerror("Erro", f"Erro ao gravar: {erro}")
            else:
                sucesso, item, erro = self.manager.adicionar_item_v2(
                    orcamento_id=self.orcamento_id,
                    secao_id=self.secao_id,
                    tipo='equipamento',
                    descricao=descricao,
                    quantidade=quantidade,
                    dias=dias,
                    preco_unitario=preco_unitario,
                    desconto=desconto_decimal,
                    equipamento_id=self.equipamento_selecionado_id
                )
                if not sucesso:
                    messagebox.showerror("Erro", f"Erro ao gravar: {erro}")

            if sucesso:
                self.success = True
                self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

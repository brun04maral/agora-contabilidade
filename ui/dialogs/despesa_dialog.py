# -*- coding: utf-8 -*-
"""
DespesaDialog - Diálogo para espelhar items CLIENTE→EMPRESA em orçamentos
Dialog especial que permite selecionar items do lado CLIENTE e criar automaticamente
items EMPRESA correspondentes com repartição 50/50 entre BA e RR
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from database.models.orcamento import OrcamentoItem, PropostaItem, PropostaSecao
from decimal import Decimal


class DespesaDialog(ctk.CTkToplevel):
    """
    Diálogo para espelhar items do lado CLIENTE para o lado EMPRESA
    Permite seleção múltipla e cria automaticamente items com repartição 50/50
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        secao_id: int
    ):
        super().__init__(parent)

        self.db = db_session
        self.orcamento_id = orcamento_id
        self.secao_id = secao_id

        # Dicionário para guardar checkboxes e items
        self.checkboxes: Dict[int, ctk.CTkCheckBox] = {}
        self.items_cliente: List[PropostaItem] = []

        # Configurar janela
        self.title("Espelhar Items CLIENTE → EMPRESA")
        self.geometry("900x600")
        self.resizable(True, True)

        # Tornar modal
        self.transient(parent)
        self.grab_set()

        # Centrar na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"900x600+{x}+{y}")

        self.create_widgets()
        self.load_items_cliente()

    def create_widgets(self):
        """Cria widgets do diálogo"""

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="💸 Espelhar Despesas: CLIENTE → EMPRESA",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=(0, 10))

        # Instrução
        instrucao_label = ctk.CTkLabel(
            main_frame,
            text="Selecione os items do lado CLIENTE para criar automaticamente items EMPRESA com repartição 50/50 (BA/RR)",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        instrucao_label.pack(pady=(0, 15))

        # Scrollable frame para lista de items
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame)
        self.scroll_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Header da tabela
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(header_frame, text="✓", width=40, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(5, 0))
        ctk.CTkLabel(header_frame, text="Secção", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Descrição", width=250, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Qtd", width=60, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Dias", width=60, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Valor Unit.", width=90, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Total", width=90, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        # Separador
        separator = ctk.CTkFrame(self.scroll_frame, height=2, fg_color="gray")
        separator.pack(fill="x", pady=(0, 10))

        # Container para items (será preenchido depois)
        self.items_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.items_container.pack(fill="both", expand=True)

        # Buttons frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        # Botão Selecionar Todos
        select_all_btn = ctk.CTkButton(
            btn_frame,
            text="☑ Selecionar Todos",
            command=self.select_all,
            width=140,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        select_all_btn.pack(side="left")

        # Botão Limpar Seleção
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="☐ Limpar Seleção",
            command=self.clear_selection,
            width=140,
            height=35,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        clear_btn.pack(side="left", padx=(10, 0))

        # Espaçador
        ctk.CTkLabel(btn_frame, text="").pack(side="left", expand=True)

        # Botão Cancelar
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

        # Botão Espelhar
        mirror_btn = ctk.CTkButton(
            btn_frame,
            text="✨ Espelhar Selecionados",
            command=self.mirror_selected,
            width=180,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        mirror_btn.pack(side="right", padx=(0, 10))

    def load_items_cliente(self):
        """Carrega items do lado CLIENTE e popula a lista"""
        # Buscar items da proposta (lado CLIENTE)
        self.items_cliente = self.db.query(PropostaItem).filter(
            PropostaItem.orcamento_id == self.orcamento_id
        ).order_by(PropostaItem.secao_id, PropostaItem.ordem).all()

        if not self.items_cliente:
            # Mostrar mensagem se não houver items
            no_items_label = ctk.CTkLabel(
                self.items_container,
                text="⚠️ Nenhum item encontrado no lado CLIENTE.\nAdicione items à proposta primeiro.",
                font=ctk.CTkFont(size=14),
                text_color="orange"
            )
            no_items_label.pack(pady=50)
            return

        # Criar linha para cada item
        for item in self.items_cliente:
            self.create_item_row(item)

    def create_item_row(self, item: PropostaItem):
        """Cria uma linha na tabela para um item"""
        row_frame = ctk.CTkFrame(self.items_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        # Checkbox
        checkbox = ctk.CTkCheckBox(row_frame, text="", width=40)
        checkbox.pack(side="left", padx=(5, 0))
        self.checkboxes[item.id] = checkbox

        # Obter nome da secção
        secao = self.db.query(PropostaSecao).filter(PropostaSecao.id == item.secao_id).first()
        secao_nome = secao.nome if secao else "N/A"

        # Secção
        ctk.CTkLabel(row_frame, text=secao_nome[:18], width=120).pack(side="left", padx=5)

        # Descrição (truncada)
        descricao_truncada = item.descricao[:40] + "..." if len(item.descricao) > 40 else item.descricao
        ctk.CTkLabel(row_frame, text=descricao_truncada, width=250, anchor="w").pack(side="left", padx=5)

        # Quantidade
        ctk.CTkLabel(row_frame, text=str(item.quantidade), width=60).pack(side="left", padx=5)

        # Dias
        ctk.CTkLabel(row_frame, text=str(item.dias), width=60).pack(side="left", padx=5)

        # Valor Unitário
        ctk.CTkLabel(row_frame, text=f"{float(item.preco_unitario):.2f}€", width=90).pack(side="left", padx=5)

        # Total
        ctk.CTkLabel(
            row_frame,
            text=f"{float(item.total):.2f}€",
            width=90,
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=5)

    def select_all(self):
        """Seleciona todos os checkboxes"""
        for checkbox in self.checkboxes.values():
            checkbox.select()

    def clear_selection(self):
        """Limpa todos os checkboxes"""
        for checkbox in self.checkboxes.values():
            checkbox.deselect()

    def get_selected_items(self) -> List[PropostaItem]:
        """Retorna lista de items selecionados"""
        selected = []
        for item_id, checkbox in self.checkboxes.items():
            if checkbox.get():  # Se checkbox está selecionado
                item = next((i for i in self.items_cliente if i.id == item_id), None)
                if item:
                    selected.append(item)
        return selected

    def check_if_already_mirrored(self, item_cliente: PropostaItem) -> bool:
        """Verifica se um item já foi espelhado (para evitar duplicados)"""
        # Verificar se já existe item EMPRESA com descrição e valor similares
        existing = self.db.query(OrcamentoItem).filter(
            OrcamentoItem.orcamento_id == self.orcamento_id,
            OrcamentoItem.secao_id == self.secao_id,
            OrcamentoItem.descricao == item_cliente.descricao
        ).first()

        return existing is not None

    def mirror_selected(self):
        """Espelha items selecionados do lado CLIENTE para o lado EMPRESA"""
        selected_items = self.get_selected_items()

        if not selected_items:
            messagebox.showwarning("Aviso", "Por favor, selecione pelo menos 1 item para espelhar.")
            return

        # Confirmar ação
        confirmacao = messagebox.askyesno(
            "Confirmar Espelhamento",
            f"Espelhar {len(selected_items)} item(s) do lado CLIENTE para EMPRESA?\n\n"
            "Cada item será dividido 50/50 entre BA e RR."
        )

        if not confirmacao:
            return

        # Espelhar items
        items_espelhados = 0
        items_ignorados = 0
        errors = []

        try:
            for item_cliente in selected_items:
                # Verificar se já foi espelhado
                if self.check_if_already_mirrored(item_cliente):
                    items_ignorados += 1
                    continue

                # Obter próxima ordem
                ultimo_item = self.db.query(OrcamentoItem).filter(
                    OrcamentoItem.secao_id == self.secao_id
                ).order_by(OrcamentoItem.ordem.desc()).first()

                ordem_base = (ultimo_item.ordem + 1) if ultimo_item else 0

                # Calcular metade do valor
                valor_metade = Decimal(str(float(item_cliente.total) / 2))

                # Criar item para BA (50%)
                item_ba = OrcamentoItem(
                    orcamento_id=self.orcamento_id,
                    secao_id=self.secao_id,
                    descricao=item_cliente.descricao,
                    afetacao="BA",
                    quantidade=item_cliente.quantidade,
                    dias=item_cliente.dias,
                    preco_unitario=Decimal(str(float(item_cliente.preco_unitario) / 2)),
                    desconto=item_cliente.desconto,
                    total=valor_metade,
                    ordem=ordem_base
                )
                self.db.add(item_ba)

                # Criar item para RR (50%)
                item_rr = OrcamentoItem(
                    orcamento_id=self.orcamento_id,
                    secao_id=self.secao_id,
                    descricao=item_cliente.descricao,
                    afetacao="RR",
                    quantidade=item_cliente.quantidade,
                    dias=item_cliente.dias,
                    preco_unitario=Decimal(str(float(item_cliente.preco_unitario) / 2)),
                    desconto=item_cliente.desconto,
                    total=valor_metade,
                    ordem=ordem_base + 1
                )
                self.db.add(item_rr)

                items_espelhados += 2  # 2 items criados (BA + RR)

            self.db.commit()

            # Mensagem de sucesso
            mensagem = f"✅ {items_espelhados} item(s) espelhado(s) com sucesso!"
            if items_ignorados > 0:
                mensagem += f"\n⚠️ {items_ignorados} item(s) ignorado(s) (já espelhados anteriormente)"

            messagebox.showinfo("Sucesso", mensagem)
            self.destroy()

        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Erro", f"Erro ao espelhar items: {str(e)}")

# -*- coding: utf-8 -*-
"""
PropostaItemDialog - Diálogo para adicionar/editar items da proposta (versão cliente)
Versão simplificada sem campos económicos internos
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from sqlalchemy.orm import Session
from database.models.orcamento import PropostaSecao, PropostaItem


class PropostaItemDialog(ctk.CTkToplevel):
    """
    Diálogo para adicionar ou editar item da proposta
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        item: Optional[PropostaItem] = None
    ):
        super().__init__(parent)

        self.db = db_session
        self.orcamento_id = orcamento_id
        self.item = item
        self.is_edit = item is not None

        # Configurar janela
        self.title("Editar Item da Proposta" if self.is_edit else "Adicionar Item à Proposta")
        self.geometry("600x650")
        self.resizable(False, False)

        # Tornar modal
        self.transient(parent)
        self.grab_set()

        # Centrar na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f"600x650+{x}+{y}")

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
            text="📋 " + ("Editar Item da Proposta" if self.is_edit else "Novo Item da Proposta"),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=(0, 20))

        # Scrollable form
        scroll = ctk.CTkScrollableFrame(main_frame)
        scroll.pack(fill="both", expand=True)

        # Secção *
        ctk.CTkLabel(scroll, text="Secção *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))

        # Frame para secção com botão de criar
        secao_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        secao_frame.pack(fill="x", pady=(0, 10))

        # Carregar secções existentes
        secoes = self.db.query(PropostaSecao).filter(
            PropostaSecao.orcamento_id == self.orcamento_id
        ).order_by(PropostaSecao.ordem).all()

        secao_names = [s.nome for s in secoes]
        self.secoes_map = {s.nome: s.id for s in secoes}

        self.secao_combo = ctk.CTkComboBox(
            secao_frame,
            values=secao_names if secao_names else ["Criar nova secção..."],
            height=35,
            state="readonly" if secao_names else "disabled"
        )
        self.secao_combo.pack(side="left", fill="x", expand=True, padx=(0, 5))

        if secao_names:
            self.secao_combo.set(secao_names[0])

        # Botão para criar nova secção
        nova_secao_btn = ctk.CTkButton(
            secao_frame,
            text="➕ Nova Secção",
            command=self.criar_nova_secao,
            width=120,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        nova_secao_btn.pack(side="right")

        # Descrição *
        ctk.CTkLabel(scroll, text="Descrição *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.descricao_textbox = ctk.CTkTextbox(scroll, height=80)
        self.descricao_textbox.pack(fill="x", pady=(0, 10))

        # Quantidade e Dias (lado a lado)
        qtd_dias_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        qtd_dias_frame.pack(fill="x", pady=(10, 10))

        # Quantidade
        qtd_col = ctk.CTkFrame(qtd_dias_frame, fg_color="transparent")
        qtd_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(qtd_col, text="Quantidade *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.quantidade_entry = ctk.CTkEntry(qtd_col, placeholder_text="Ex: 1", height=35)
        self.quantidade_entry.pack(fill="x")
        self.quantidade_entry.insert(0, "1")
        self.quantidade_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Dias
        dias_col = ctk.CTkFrame(qtd_dias_frame, fg_color="transparent")
        dias_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(dias_col, text="Dias *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 5))
        self.dias_entry = ctk.CTkEntry(dias_col, placeholder_text="Ex: 1", height=35)
        self.dias_entry.pack(fill="x")
        self.dias_entry.insert(0, "1")
        self.dias_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Preço Unitário *
        ctk.CTkLabel(scroll, text="Preço Unitário (€) *", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.preco_entry = ctk.CTkEntry(scroll, placeholder_text="Ex: 100.00", height=35)
        self.preco_entry.pack(fill="x", pady=(0, 10))
        self.preco_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

        # Desconto (%)
        ctk.CTkLabel(scroll, text="Desconto (%)", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(10, 5))
        self.desconto_entry = ctk.CTkEntry(scroll, placeholder_text="Ex: 10", height=35)
        self.desconto_entry.pack(fill="x", pady=(0, 10))
        self.desconto_entry.insert(0, "0")
        self.desconto_entry.bind("<KeyRelease>", lambda e: self.calcular_total())

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

    def criar_nova_secao(self):
        """Cria uma nova secção"""
        dialog = ctk.CTkInputDialog(
            text="Nome da nova secção:",
            title="Nova Secção da Proposta"
        )
        nome = dialog.get_input()

        if not nome:
            return

        # Criar secção
        try:
            # Obter próxima ordem
            ultima_secao = self.db.query(PropostaSecao).filter(
                PropostaSecao.orcamento_id == self.orcamento_id
            ).order_by(PropostaSecao.ordem.desc()).first()

            ordem = (ultima_secao.ordem + 1) if ultima_secao else 0

            nova_secao = PropostaSecao(
                orcamento_id=self.orcamento_id,
                nome=nome,
                ordem=ordem
            )

            self.db.add(nova_secao)
            self.db.commit()

            # Atualizar combobox
            secoes = self.db.query(PropostaSecao).filter(
                PropostaSecao.orcamento_id == self.orcamento_id
            ).order_by(PropostaSecao.ordem).all()

            secao_names = [s.nome for s in secoes]
            self.secoes_map = {s.nome: s.id for s in secoes}

            self.secao_combo.configure(values=secao_names, state="readonly")
            self.secao_combo.set(nome)

            messagebox.showinfo("Sucesso", f"Secção '{nome}' criada com sucesso!")
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Erro", f"Erro ao criar secção: {str(e)}")

    def calcular_total(self):
        """Calcula o total do item"""
        try:
            quantidade = int(self.quantidade_entry.get() or 0)
            dias = int(self.dias_entry.get() or 0)
            preco = float(self.preco_entry.get() or 0)
            desconto_pct = float(self.desconto_entry.get() or 0)

            # Calcular total
            subtotal = quantidade * dias * preco
            desconto_valor = subtotal * (desconto_pct / 100)
            total = subtotal - desconto_valor

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

        # Selecionar secção
        secao = self.db.query(PropostaSecao).filter(
            PropostaSecao.id == self.item.secao_id
        ).first()

        if secao:
            self.secao_combo.set(secao.nome)

        # Preencher campos
        self.descricao_textbox.insert("1.0", self.item.descricao)
        self.quantidade_entry.delete(0, "end")
        self.quantidade_entry.insert(0, str(self.item.quantidade))
        self.dias_entry.delete(0, "end")
        self.dias_entry.insert(0, str(self.item.dias))
        self.preco_entry.delete(0, "end")
        self.preco_entry.insert(0, str(float(self.item.preco_unitario)))
        self.desconto_entry.delete(0, "end")
        self.desconto_entry.insert(0, str(float(self.item.desconto) * 100))

        # Calcular total
        self.calcular_total()

    def save(self):
        """Guarda item da proposta"""
        # Validação
        secao_nome = self.secao_combo.get()
        if not secao_nome or secao_nome == "Criar nova secção...":
            messagebox.showerror("Erro", "Por favor, selecione ou crie uma secção.")
            return

        descricao = self.descricao_textbox.get("1.0", "end").strip()
        if not descricao:
            messagebox.showerror("Erro", "Por favor, preencha a descrição.")
            return

        try:
            quantidade = int(self.quantidade_entry.get())
            dias = int(self.dias_entry.get())
            preco_unitario = float(self.preco_entry.get())
            desconto_pct = float(self.desconto_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos.")
            return

        # Calcular total
        desconto_decimal = desconto_pct / 100
        total = (quantidade * dias * preco_unitario) * (1 - desconto_decimal)

        # Obter secao_id
        secao_id = self.secoes_map.get(secao_nome)
        if not secao_id:
            messagebox.showerror("Erro", "Secção inválida.")
            return

        try:
            if self.is_edit:
                # Atualizar item existente
                self.item.secao_id = secao_id
                self.item.descricao = descricao
                self.item.quantidade = quantidade
                self.item.dias = dias
                self.item.preco_unitario = preco_unitario
                self.item.desconto = desconto_decimal
                self.item.total = total
            else:
                # Criar novo item
                # Obter próxima ordem
                ultimo_item = self.db.query(PropostaItem).filter(
                    PropostaItem.secao_id == secao_id
                ).order_by(PropostaItem.ordem.desc()).first()

                ordem = (ultimo_item.ordem + 1) if ultimo_item else 0

                novo_item = PropostaItem(
                    orcamento_id=self.orcamento_id,
                    secao_id=secao_id,
                    descricao=descricao,
                    quantidade=quantidade,
                    dias=dias,
                    preco_unitario=preco_unitario,
                    desconto=desconto_decimal,
                    total=total,
                    ordem=ordem
                )
                self.db.add(novo_item)

            self.db.commit()

            # Recalcular subtotal da secção
            secao = self.db.query(PropostaSecao).filter(
                PropostaSecao.id == secao_id
            ).first()

            if secao:
                itens = self.db.query(PropostaItem).filter(
                    PropostaItem.secao_id == secao_id
                ).all()
                secao.subtotal = sum(float(item.total) for item in itens)
                self.db.commit()

            messagebox.showinfo("Sucesso", "Item guardado com sucesso!")
            self.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Erro", f"Erro ao guardar item: {str(e)}")

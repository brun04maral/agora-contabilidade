# -*- coding: utf-8 -*-
"""
EquipamentoEmpresaDialog - Dialog para criar/editar equipamento EMPRESA (LADO EMPRESA)
"""
import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from logic.freelancers import FreelancersManager
from logic.fornecedores import FornecedoresManager
from database.models.orcamento import OrcamentoReparticao
from decimal import Decimal
from typing import Optional, Dict


class EquipamentoEmpresaDialog(ctk.CTkToplevel):
    """
    Dialog para adicionar/editar equipamento no LADO EMPRESA

    Campos:
    - Beneficiário (dropdown obrigatório: BA, RR, AGORA, FREELANCER_[id], FORNECEDOR_[id])
    - Descrição (obrigatório)
    - Quantidade (inteiro, obrigatório)
    - Dias (inteiro, obrigatório)
    - Valor Unitário (decimal, obrigatório)

    Cálculo:
    total = quantidade × dias × valor_unitário
    (SEM desconto no lado EMPRESA)

    Beneficiários:
    - Sócios: BA, RR, AGORA
    - Freelancers: FREELANCER_{id} (apenas ativos)
    - Fornecedores: FORNECEDOR_{id} (apenas ativos)
    """

    def __init__(
        self,
        parent,
        db_session: Session,
        orcamento_id: int,
        item_id: Optional[int] = None
    ):
        super().__init__(parent)

        self.db_session = db_session
        self.manager = OrcamentoManager(db_session)
        self.freelancers_manager = FreelancersManager(db_session)
        self.fornecedores_manager = FornecedoresManager(db_session)
        self.orcamento_id = orcamento_id
        self.item_id = item_id
        self.success = False

        # Mapeamento beneficiários: {id: display_name}
        self.beneficiarios_map: Dict[str, str] = {}
        self._carregar_beneficiarios()

        # Configurar janela
        self.title("Adicionar Equipamento EMPRESA" if not item_id else "Editar Equipamento EMPRESA")
        self.geometry("500x580")
        self.resizable(False, False)

        # Modal
        self.transient(parent)
        self.grab_set()

        # Criar widgets
        self.create_widgets()

        # Se edição, carregar dados
        if item_id:
            self.carregar_dados()

    def _carregar_beneficiarios(self):
        """Carrega beneficiários de múltiplas fontes"""
        # Sócios fixos
        self.beneficiarios_map["BA"] = "BA - Bruno Amaral"
        self.beneficiarios_map["RR"] = "RR - Rafael Ribeiro"
        self.beneficiarios_map["AGORA"] = "AGORA - Empresa"

        # Freelancers ativos
        try:
            freelancers = self.freelancers_manager.listar_ativos()
            for freelancer in freelancers:
                key = f"FREELANCER_{freelancer.id}"
                self.beneficiarios_map[key] = f"{key} - {freelancer.nome}"
        except:
            pass  # Tabela pode não existir ainda

        # Fornecedores ativos
        try:
            fornecedores = self.fornecedores_manager.listar_ativos()
            for fornecedor in fornecedores:
                key = f"FORNECEDOR_{fornecedor.id}"
                self.beneficiarios_map[key] = f"{key} - {fornecedor.nome}"
        except:
            pass  # Tabela pode não existir ainda

    def create_widgets(self):
        """Cria widgets do dialog"""
        # Container principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Equipamento - LADO EMPRESA",
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

        # Valores do dropdown: display_name (mas guardamos id interno)
        dropdown_values = list(self.beneficiarios_map.values())

        self.beneficiario_var = ctk.StringVar(value="")
        self.beneficiario_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=self.beneficiario_var,
            values=dropdown_values if dropdown_values else ["BA - Bruno Amaral", "RR - Rafael Ribeiro", "AGORA - Empresa"],
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
            placeholder_text="Ex: Câmara Sony FX3",
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
            placeholder_text="Ex: 4",
            height=35
        )
        self.quantidade_entry.pack(fill="x")

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
            placeholder_text="Ex: 2",
            height=35
        )
        self.dias_entry.pack(fill="x")

        # Valor Unitário
        ctk.CTkLabel(
            main_frame,
            text="Valor Unitário (€):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.valor_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Ex: 50.00",
            height=35
        )
        self.valor_entry.pack(fill="x", pady=(0, 20))

        # Nota informativa
        ctk.CTkLabel(
            main_frame,
            text="ℹ️ Sem desconto no lado EMPRESA",
            font=ctk.CTkFont(size=11),
            text_color=("#666", "#999")
        ).pack(pady=(0, 20))

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
            fg_color="#2196F3",
            hover_color="#0b7dda"
        )
        btn_gravar.pack(side="right")

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
            # Encontrar display name correspondente ao id
            display_name = self.beneficiarios_map.get(item.beneficiario, item.beneficiario)
            self.beneficiario_var.set(display_name)

        if item.descricao:
            self.descricao_entry.delete(0, "end")
            self.descricao_entry.insert(0, item.descricao)

        if item.quantidade:
            self.quantidade_entry.delete(0, "end")
            self.quantidade_entry.insert(0, str(item.quantidade))

        if item.dias:
            self.dias_entry.delete(0, "end")
            self.dias_entry.insert(0, str(item.dias))

        if item.valor_unitario:
            self.valor_entry.delete(0, "end")
            self.valor_entry.insert(0, str(float(item.valor_unitario)))

    def gravar(self):
        """Grava o equipamento EMPRESA"""
        try:
            # Validar beneficiário (OBRIGATÓRIO)
            beneficiario_display = self.beneficiario_var.get()
            if not beneficiario_display:
                messagebox.showwarning("Aviso", "Beneficiário é obrigatório!")
                return

            # Extrair ID do beneficiário (reverse lookup no mapa)
            beneficiario_id = None
            for key, value in self.beneficiarios_map.items():
                if value == beneficiario_display:
                    beneficiario_id = key
                    break

            if not beneficiario_id:
                messagebox.showerror("Erro", "Beneficiário inválido!")
                return

            # Validar beneficiário (freelancer/fornecedor deve existir e estar ativo)
            if beneficiario_id.startswith("FREELANCER_"):
                freelancer_id = int(beneficiario_id.replace("FREELANCER_", ""))
                freelancer = self.freelancers_manager.buscar_por_id(freelancer_id)
                if not freelancer or not freelancer.ativo:
                    messagebox.showerror("Erro", "Freelancer não encontrado ou inativo!")
                    return
            elif beneficiario_id.startswith("FORNECEDOR_"):
                fornecedor_id = int(beneficiario_id.replace("FORNECEDOR_", ""))
                fornecedor = self.fornecedores_manager.buscar_por_id(fornecedor_id)
                if not fornecedor:
                    messagebox.showerror("Erro", "Fornecedor não encontrado!")
                    return

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

            # Validar valor unitário
            valor_str = self.valor_entry.get().strip()
            if not valor_str:
                messagebox.showwarning("Aviso", "Valor unitário é obrigatório!")
                return

            # Converter valores
            try:
                quantidade = int(quantidade_str)
                dias = int(dias_str)
                valor_unitario = Decimal(valor_str.replace(',', '.'))
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

            if valor_unitario <= 0:
                messagebox.showwarning("Aviso", "Valor unitário deve ser maior que 0!")
                return

            # Gravar no banco (usar beneficiario_id)
            if self.item_id:
                # Editar existente
                sucesso, item, erro = self.manager.atualizar_reparticao(
                    reparticao_id=self.item_id,
                    tipo='equipamento',
                    beneficiario=beneficiario_id,  # Usar ID (BA, FREELANCER_2, FORNECEDOR_5, etc)
                    descricao=descricao,
                    quantidade=quantidade,
                    dias=dias,
                    valor_unitario=valor_unitario
                )
                if sucesso:
                    item.total = item.calcular_total()
                    self.db_session.commit()
            else:
                # Criar novo
                reparticao = OrcamentoReparticao(
                    orcamento_id=self.orcamento_id,
                    tipo='equipamento',
                    beneficiario=beneficiario_id,  # Usar ID (BA, FREELANCER_2, FORNECEDOR_5, etc)
                    descricao=descricao,
                    quantidade=quantidade,
                    dias=dias,
                    valor_unitario=valor_unitario,
                    total=Decimal('0')
                )
                reparticao.total = reparticao.calcular_total()
                self.db_session.add(reparticao)
                self.db_session.commit()
                sucesso = True

            if sucesso:
                self.success = True
                messagebox.showinfo("Sucesso", "Equipamento EMPRESA gravado com sucesso!")
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro ao gravar: {erro if 'erro' in locals() else 'Desconhecido'}")

        except Exception as e:
            self.db_session.rollback()
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

# -*- coding: utf-8 -*-
"""
Tela de Formulário de Orçamento V2 - ARQUITETURA CLIENTE/EMPRESA
Sistema dual: LADO CLIENTE (proposta comercial) + LADO EMPRESA (repartição interna)

Referências:
- /memory/BUSINESS_LOGIC.md (Secção 1-7)
- /memory/DATABASE_SCHEMA.md (Modelo de Dados V2)
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from logic.clientes import ClientesManager
from ui.components.autocomplete_entry import AutocompleteEntry
from ui.components.date_picker_dropdown import DatePickerDropdown
from typing import Optional
from datetime import date
from tkinter import messagebox
from decimal import Decimal


class OrcamentoFormScreen(ctk.CTkFrame):
    """
    Screen para criar/editar orçamentos - Arquitetura V2

    LADO CLIENTE: Proposta comercial (o que o cliente vê e paga)
    LADO EMPRESA: Repartição interna (como a receita é distribuída)

    REGRA FUNDAMENTAL: TOTAL_CLIENTE deve ser IGUAL a TOTAL_EMPRESA
    """

    def __init__(self, parent, db_session: Session, orcamento_id: Optional[int] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.orcamento_id = orcamento_id
        self.manager = OrcamentoManager(db_session)
        self.clientes_manager = ClientesManager(db_session)

        # Estado
        self.orcamento = None
        self.alteracoes_pendentes = False
        self.clientes_map = {}

        # Caches para evitar recálculos
        self._total_cliente = Decimal('0')
        self._total_empresa = Decimal('0')

        # Configure
        self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.create_widgets()

        # Load data se edição
        if orcamento_id:
            self.carregar_orcamento()
        else:
            # Gerar código automático para novo orçamento
            self.codigo_entry.configure(state="normal")
            self.codigo_entry.delete(0, "end")
            self.codigo_entry.insert(0, self.manager.gerar_proximo_codigo())
            self.codigo_entry.configure(state="disabled")

    def create_widgets(self):
        """Cria widgets da screen"""
        # Container principal com scroll
        main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_container.grid_columnconfigure(0, weight=1)

        # ========================================
        # 1. HEADER
        # ========================================
        self.create_header(main_container)

        # ========================================
        # 2. CAMPOS DO ORÇAMENTO
        # ========================================
        self.create_fields(main_container)

        # ========================================
        # 3. TABS CLIENTE/EMPRESA
        # ========================================
        self.create_tabs(main_container)

        # ========================================
        # 4. FOOTER COM BOTÕES
        # ========================================
        self.create_footer(main_container)

    def create_header(self, parent):
        """Cria header com botão voltar, título e badge de estado"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        header_frame.grid_columnconfigure(1, weight=1)

        # Botão voltar
        voltar_btn = ctk.CTkButton(
            header_frame,
            text="⬅️ Voltar",
            command=self.voltar,
            width=100,
            height=35,
            fg_color="gray",
            hover_color="#5a5a5a"
        )
        voltar_btn.grid(row=0, column=0, sticky="w", padx=(0, 20))

        # Título
        titulo = "Novo Orçamento" if not self.orcamento_id else f"Editar Orçamento"
        title_label = ctk.CTkLabel(
            header_frame,
            text=titulo,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=1, sticky="w")

        # Badge de estado
        self.estado_badge = ctk.CTkLabel(
            header_frame,
            text="RASCUNHO",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#e0e0e0", "#3a3a3a"),
            text_color=("#2c3e50", "#ecf0f1"),
            corner_radius=6,
            padx=12,
            pady=6
        )
        self.estado_badge.grid(row=0, column=2, sticky="e", padx=(20, 0))

    def create_fields(self, parent):
        """Cria campos do orçamento (Header fields)"""
        fields_frame = ctk.CTkFrame(parent, fg_color=("#f0f0f0", "#2b2b2b"))
        fields_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))

        # Grid layout 4 colunas (label, field, label, field)
        for i in range(4):
            fields_frame.grid_columnconfigure(i, weight=1 if i % 2 == 1 else 0)

        # Row 0: Código | Owner
        ctk.CTkLabel(fields_frame, text="Código:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="w"
        )
        self.codigo_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Gerado automaticamente...",
            state="disabled",
            height=35
        )
        self.codigo_entry.grid(row=0, column=1, padx=(0, 20), pady=(20, 10), sticky="ew")

        ctk.CTkLabel(fields_frame, text="Owner:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=2, padx=(20, 10), pady=(20, 10), sticky="w"
        )
        self.owner_var = ctk.StringVar(value="BA")
        self.owner_dropdown = ctk.CTkOptionMenu(
            fields_frame,
            variable=self.owner_var,
            values=["BA", "RR"],
            width=120,
            height=35
        )
        self.owner_dropdown.grid(row=0, column=3, padx=(0, 20), pady=(20, 10), sticky="w")

        # Row 1: Cliente | Data Criação
        ctk.CTkLabel(fields_frame, text="Cliente:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=1, column=0, padx=(20, 10), pady=(0, 10), sticky="w"
        )
        self.cliente_autocomplete = self.create_cliente_autocomplete(fields_frame)
        self.cliente_autocomplete.grid(row=1, column=1, padx=(0, 20), pady=(0, 10), sticky="ew")

        ctk.CTkLabel(fields_frame, text="Data Criação:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=1, column=2, padx=(20, 10), pady=(0, 10), sticky="w"
        )
        self.data_criacao_picker = DatePickerDropdown(fields_frame, initial_date=date.today())
        self.data_criacao_picker.grid(row=1, column=3, padx=(0, 20), pady=(0, 10), sticky="ew")

        # Row 2: Data Evento | Local Evento
        ctk.CTkLabel(fields_frame, text="Data Evento:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=2, column=0, padx=(20, 10), pady=(0, 10), sticky="w"
        )
        self.data_evento_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ex: 15-20/11/2025",
            height=35
        )
        self.data_evento_entry.grid(row=2, column=1, padx=(0, 20), pady=(0, 10), sticky="ew")

        ctk.CTkLabel(fields_frame, text="Local Evento:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=2, column=2, padx=(20, 10), pady=(0, 20), sticky="w"
        )
        self.local_evento_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ex: Centro de Congressos",
            height=35
        )
        self.local_evento_entry.grid(row=2, column=3, padx=(0, 20), pady=(0, 20), sticky="ew")

    def create_cliente_autocomplete(self, parent):
        """Cria autocomplete para clientes"""
        # Carregar clientes
        clientes = self.clientes_manager.listar_todos()

        # Criar map de clientes
        self.clientes_map = {}
        clientes_list = []
        for cliente in clientes:
            key = f"{cliente.numero} - {cliente.nome}"
            self.clientes_map[key] = cliente.id
            clientes_list.append(key)

        # Criar autocomplete
        autocomplete = AutocompleteEntry(
            parent,
            completevalues=clientes_list,
            placeholder="Digite para pesquisar cliente...",
            height=35
        )

        return autocomplete

    def create_tabs(self, parent):
        """Cria tabs CLIENTE e EMPRESA"""
        # TabView
        self.tabview = ctk.CTkTabview(parent, height=500)
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 20))

        # Tab CLIENTE
        self.tab_cliente = self.tabview.add("👤 CLIENTE")
        self.create_tab_cliente()

        # Tab EMPRESA
        self.tab_empresa = self.tabview.add("🏢 EMPRESA")
        self.create_tab_empresa()

    def create_tab_cliente(self):
        """Cria conteúdo da Tab CLIENTE"""
        # Header com botões por secção
        header_frame = ctk.CTkFrame(self.tab_cliente, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Botões para adicionar items por tipo de secção
        btn_servicos = ctk.CTkButton(
            header_frame,
            text="➕ Serviços",
            command=lambda: self.adicionar_item_cliente('servicos'),
            width=130,
            height=32,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        btn_servicos.pack(side="left", padx=(0, 10))

        btn_equipamento = ctk.CTkButton(
            header_frame,
            text="➕ Equipamento",
            command=lambda: self.adicionar_item_cliente('equipamento'),
            width=140,
            height=32,
            fg_color="#2196F3",
            hover_color="#0b7dda"
        )
        btn_equipamento.pack(side="left", padx=(0, 10))

        btn_despesas = ctk.CTkButton(
            header_frame,
            text="➕ Despesas",
            command=lambda: self.adicionar_item_cliente('despesas'),
            width=130,
            height=32,
            fg_color="#FF9800",
            hover_color="#e68900"
        )
        btn_despesas.pack(side="left")

        # Área scrollável para items
        self.cliente_scroll = ctk.CTkScrollableFrame(
            self.tab_cliente,
            fg_color="transparent"
        )
        self.cliente_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Total CLIENTE (sempre no fundo)
        total_frame = ctk.CTkFrame(self.tab_cliente, fg_color=("#e8f5e0", "#2b4a2b"))
        total_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        self.total_cliente_label = ctk.CTkLabel(
            total_frame,
            text="TOTAL CLIENTE: €0,00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#4A7028", "#90EE90")
        )
        self.total_cliente_label.pack(pady=15)

    def create_tab_empresa(self):
        """Cria conteúdo da Tab EMPRESA"""
        # Header com botões
        header_frame = ctk.CTkFrame(self.tab_empresa, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Botões para adicionar items empresa
        btn_servico_emp = ctk.CTkButton(
            header_frame,
            text="➕ Serviço",
            command=lambda: self.adicionar_item_empresa('servico'),
            width=120,
            height=32,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        btn_servico_emp.pack(side="left", padx=(0, 10))

        btn_equip_emp = ctk.CTkButton(
            header_frame,
            text="➕ Equipamento",
            command=lambda: self.adicionar_item_empresa('equipamento'),
            width=140,
            height=32,
            fg_color="#2196F3",
            hover_color="#0b7dda"
        )
        btn_equip_emp.pack(side="left", padx=(0, 10))

        btn_comissao = ctk.CTkButton(
            header_frame,
            text="⚡ Auto-preencher Comissões",
            command=self.auto_preencher_comissoes,
            width=200,
            height=32,
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        )
        btn_comissao.pack(side="left")

        # Área scrollável para items empresa
        self.empresa_scroll = ctk.CTkScrollableFrame(
            self.tab_empresa,
            fg_color="transparent"
        )
        self.empresa_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Total EMPRESA + Validação
        total_frame = ctk.CTkFrame(self.tab_empresa, fg_color=("#e8f5e0", "#2b4a2b"))
        total_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        self.total_empresa_label = ctk.CTkLabel(
            total_frame,
            text="TOTAL EMPRESA: €0,00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#4A7028", "#90EE90")
        )
        self.total_empresa_label.pack(pady=(15, 5))

        # Label de validação (diferença)
        self.validacao_label = ctk.CTkLabel(
            total_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#f44336"
        )
        self.validacao_label.pack(pady=(0, 15))

    def create_footer(self, parent):
        """Cria footer com botões de ação"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 30))
        footer_frame.grid_columnconfigure(1, weight=1)

        # Botão Gravar Rascunho
        btn_gravar = ctk.CTkButton(
            footer_frame,
            text="💾 Gravar Rascunho",
            command=self.gravar_rascunho,
            width=150,
            height=40,
            fg_color="#2196F3",
            hover_color="#0b7dda"
        )
        btn_gravar.grid(row=0, column=0, sticky="w")

        # Botão Aprovar
        btn_aprovar = ctk.CTkButton(
            footer_frame,
            text="✅ Aprovar Orçamento",
            command=self.aprovar_orcamento,
            width=170,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        btn_aprovar.grid(row=0, column=2, sticky="e")

    # ========================================
    # MÉTODOS DE NEGÓCIO - TAB CLIENTE
    # ========================================

    def adicionar_item_cliente(self, tipo_secao):
        """Abre dialog para adicionar item no lado CLIENTE"""
        # TODO: Implementar dialogs específicos por tipo
        messagebox.showinfo("Em desenvolvimento", f"Dialog para adicionar item em secção: {tipo_secao}")

    def carregar_items_cliente(self):
        """Carrega e renderiza todos os items do LADO CLIENTE"""
        if not self.orcamento_id:
            return

        # Limpar área
        for widget in self.cliente_scroll.winfo_children():
            widget.destroy()

        # TODO: Carregar items do banco de dados
        # TODO: Renderizar por secção (Serviços, Equipamento, Despesas)
        # TODO: Calcular subtotais

        self.atualizar_total_cliente()

    def atualizar_total_cliente(self):
        """Atualiza TOTAL CLIENTE"""
        if not self.orcamento_id:
            self._total_cliente = Decimal('0')
            self.total_cliente_label.configure(text="TOTAL CLIENTE: €0,00")
            return

        # TODO: Calcular total real dos items
        self._total_cliente = Decimal('0')
        self.total_cliente_label.configure(text=f"TOTAL CLIENTE: €{float(self._total_cliente):.2f}")

        # Validar contra TOTAL EMPRESA
        self.validar_totais()

    # ========================================
    # MÉTODOS DE NEGÓCIO - TAB EMPRESA
    # ========================================

    def adicionar_item_empresa(self, tipo):
        """Abre dialog para adicionar item no lado EMPRESA"""
        # TODO: Implementar dialogs específicos por tipo
        messagebox.showinfo("Em desenvolvimento", f"Dialog para adicionar item EMPRESA tipo: {tipo}")

    def auto_preencher_comissoes(self):
        """Auto-preenche comissões com valores padrão"""
        if not self.orcamento_id:
            messagebox.showwarning("Aviso", "Grave o orçamento primeiro!")
            return

        # TODO: Implementar lógica de auto-preenchimento
        messagebox.showinfo("Em desenvolvimento", "Auto-preenchimento de comissões será implementado")

    def carregar_items_empresa(self):
        """Carrega e renderiza todos os items do LADO EMPRESA"""
        if not self.orcamento_id:
            return

        # Limpar área
        for widget in self.empresa_scroll.winfo_children():
            widget.destroy()

        # TODO: Carregar items empresa do banco de dados
        # TODO: Carregar despesas espelhadas (readonly)
        # TODO: Carregar comissões

        self.atualizar_total_empresa()

    def atualizar_total_empresa(self):
        """Atualiza TOTAL EMPRESA"""
        if not self.orcamento_id:
            self._total_empresa = Decimal('0')
            self.total_empresa_label.configure(text="TOTAL EMPRESA: €0,00")
            return

        # TODO: Calcular total real (base + comissões)
        self._total_empresa = Decimal('0')
        self.total_empresa_label.configure(text=f"TOTAL EMPRESA: €{float(self._total_empresa):.2f}")

        # Validar contra TOTAL CLIENTE
        self.validar_totais()

    def validar_totais(self):
        """Valida se TOTAL CLIENTE == TOTAL EMPRESA"""
        diferenca = abs(self._total_cliente - self._total_empresa)

        if diferenca < Decimal('0.01'):  # Tolerância de 1 cêntimo
            # Totais coincidem
            self.validacao_label.configure(
                text="✓ Totais coincidem",
                text_color="#4CAF50"
            )
            self.total_empresa_label.configure(text_color=("#4A7028", "#90EE90"))
            return True
        else:
            # Totais NÃO coincidem
            self.validacao_label.configure(
                text=f"⚠️ DIFERENÇA: €{float(diferenca):.2f}",
                text_color="#f44336"
            )
            self.total_empresa_label.configure(text_color="#f44336")
            return False

    # ========================================
    # MÉTODOS DE PERSISTÊNCIA
    # ========================================

    def gravar_rascunho(self):
        """Grava orçamento como rascunho (sem validação de totais)"""
        try:
            # Validar campos obrigatórios
            if not self.codigo_entry.get():
                messagebox.showwarning("Aviso", "Código é obrigatório!")
                return

            owner = self.owner_var.get()
            if not owner:
                messagebox.showwarning("Aviso", "Selecione o Owner (BA ou RR)!")
                return

            cliente_key = self.cliente_autocomplete.get()
            if not cliente_key or cliente_key not in self.clientes_map:
                messagebox.showwarning("Aviso", "Selecione um cliente válido!")
                return

            cliente_id = self.clientes_map[cliente_key]

            # Preparar dados
            data = {
                "codigo": self.codigo_entry.get(),
                "owner": owner,
                "cliente_id": cliente_id,
                "data_criacao": self.data_criacao_picker.get_date(),
                "data_evento": self.data_evento_entry.get() or None,
                "local_evento": self.local_evento_entry.get() or None,
                "status": "rascunho"
            }

            if self.orcamento_id:
                # Atualizar existente
                sucesso, orcamento, erro = self.manager.atualizar_orcamento(self.orcamento_id, **data)
            else:
                # Criar novo
                sucesso, orcamento, erro = self.manager.criar_orcamento(**data)
                if sucesso:
                    self.orcamento_id = orcamento.id
                    self.orcamento = orcamento

            if sucesso:
                messagebox.showinfo("Sucesso", "Orçamento gravado como rascunho!")
                self.alteracoes_pendentes = False
                self.atualizar_estado_badge()
            else:
                messagebox.showerror("Erro", f"Erro ao gravar: {erro}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def aprovar_orcamento(self):
        """Aprova orçamento (requer validação de totais)"""
        if not self.orcamento_id:
            messagebox.showwarning("Aviso", "Grave o orçamento primeiro!")
            return

        # Validar totais
        if not self.validar_totais():
            messagebox.showerror(
                "Validação Falhou",
                "Não é possível aprovar o orçamento!\n\n"
                "TOTAL CLIENTE deve ser igual a TOTAL EMPRESA.\n"
                "Ajuste os valores ou comissões para igualar os totais."
            )
            return

        # TODO: Aprovar orçamento no manager
        messagebox.showinfo("Em desenvolvimento", "Aprovação será implementada")

    def carregar_orcamento(self):
        """Carrega dados do orçamento para edição"""
        self.orcamento = self.manager.obter_orcamento(self.orcamento_id)
        if not self.orcamento:
            messagebox.showerror("Erro", "Orçamento não encontrado!")
            self.voltar()
            return

        # Preencher campos
        self.codigo_entry.configure(state="normal")
        self.codigo_entry.delete(0, "end")
        self.codigo_entry.insert(0, self.orcamento.codigo)
        self.codigo_entry.configure(state="disabled")

        self.owner_var.set(self.orcamento.owner)

        if self.orcamento.cliente:
            cliente_key = f"{self.orcamento.cliente.numero} - {self.orcamento.cliente.nome}"
            self.cliente_autocomplete.set(cliente_key)

        if self.orcamento.data_criacao:
            self.data_criacao_picker.set_date(self.orcamento.data_criacao)

        if self.orcamento.data_evento:
            self.data_evento_entry.delete(0, "end")
            self.data_evento_entry.insert(0, self.orcamento.data_evento)

        if self.orcamento.local_evento:
            self.local_evento_entry.delete(0, "end")
            self.local_evento_entry.insert(0, self.orcamento.local_evento)

        # Atualizar estado badge
        self.atualizar_estado_badge()

        # Carregar items
        self.carregar_items_cliente()
        self.carregar_items_empresa()

        # Reset flag
        self.alteracoes_pendentes = False

    def atualizar_estado_badge(self):
        """Atualiza badge de estado visual"""
        if not self.orcamento:
            return

        status = self.orcamento.status

        if status == "aprovado":
            self.estado_badge.configure(
                text="APROVADO",
                fg_color="#4CAF50",
                text_color="white"
            )
        elif status == "rejeitado":
            self.estado_badge.configure(
                text="REJEITADO",
                fg_color="#f44336",
                text_color="white"
            )
        else:  # rascunho
            self.estado_badge.configure(
                text="RASCUNHO",
                fg_color=("#e0e0e0", "#3a3a3a"),
                text_color=("#2c3e50", "#ecf0f1")
            )

    def voltar(self):
        """Volta para listagem de orçamentos"""
        if self.alteracoes_pendentes:
            if not messagebox.askyesno(
                "Alterações Pendentes",
                "Tem alterações não gravadas. Deseja sair mesmo assim?"
            ):
                return

        # Navegar de volta
        main_window = self.master.master
        if hasattr(main_window, 'show_orcamentos'):
            main_window.show_orcamentos()


# ========================================
# TODO: Dialogs específicos por tipo
# ========================================
# - ServicoDialogCliente
# - EquipamentoDialogCliente
# - TransporteDialog (só cliente)
# - RefeicaoDialog (só cliente)
# - OutroDialog (só cliente)
# - ServicoDialogEmpresa (com beneficiário)
# - EquipamentoDialogEmpresa (com beneficiário)
# - ComissaoDialog (auto-preenchimento)

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
from ui.dialogs.transporte_dialog import TransporteDialog
from ui.dialogs.refeicao_dialog import RefeicaoDialog
from ui.dialogs.outro_dialog import OutroDialog
from ui.dialogs.servico_dialog import ServicoDialog
from ui.dialogs.equipamento_dialog import EquipamentoDialog
from ui.dialogs.servico_empresa_dialog import ServicoEmpresaDialog
from ui.dialogs.equipamento_empresa_dialog import EquipamentoEmpresaDialog
from ui.dialogs.comissao_dialog import ComissaoDialog
from database.models.orcamento import OrcamentoItem, OrcamentoReparticao
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
        self.data_criacao_picker = DatePickerDropdown(fields_frame, default_date=date.today())
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
            options=clientes_list,
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
        # Verificar se orçamento foi gravado
        if not self.orcamento_id:
            messagebox.showwarning("Aviso", "Grave o orçamento antes de adicionar items!")
            return

        # Obter secção correspondente
        secoes = self.manager.obter_secoes(self.orcamento_id)
        secao = None

        # Mapear tipo_secao para tipo de secção do banco
        if tipo_secao == 'servicos':
            secao = next((s for s in secoes if s.tipo == 'servicos'), None)
            if secao:
                self.abrir_dialog_servico_cliente(secao.id)
        elif tipo_secao == 'equipamento':
            secao = next((s for s in secoes if s.tipo == 'equipamento'), None)
            if secao:
                self.abrir_dialog_equipamento_cliente(secao.id)
        elif tipo_secao == 'despesas':
            # Para despesas, mostrar menu de escolha
            self.mostrar_menu_despesas_cliente()

        if not secao and tipo_secao != 'despesas':
            messagebox.showerror("Erro", f"Secção '{tipo_secao}' não encontrada!")

    def mostrar_menu_despesas_cliente(self):
        """Mostra menu para escolher tipo de despesa"""
        # Obter secção de despesas
        secoes = self.manager.obter_secoes(self.orcamento_id)
        secao_despesas = next((s for s in secoes if s.tipo == 'despesas'), None)

        if not secao_despesas:
            messagebox.showerror("Erro", "Secção 'Despesas' não encontrada!")
            return

        # Criar janela de escolha
        dialog = ctk.CTkToplevel(self)
        dialog.title("Escolher Tipo de Despesa")
        dialog.geometry("350x360")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Conteúdo
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="Escolha o tipo de despesa:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(0, 20))

        # Botões
        btn_transporte = ctk.CTkButton(
            main_frame,
            text="🚗 Transporte (KMs)",
            command=lambda: [dialog.destroy(), self.abrir_dialog_transporte(secao_despesas.id)],
            height=40,
            fg_color="#FF9800",
            hover_color="#e68900"
        )
        btn_transporte.pack(fill="x", pady=(0, 10))

        btn_refeicao = ctk.CTkButton(
            main_frame,
            text="🍽️ Refeições",
            command=lambda: [dialog.destroy(), self.abrir_dialog_refeicao(secao_despesas.id)],
            height=40,
            fg_color="#FF9800",
            hover_color="#e68900"
        )
        btn_refeicao.pack(fill="x", pady=(0, 10))

        btn_outro = ctk.CTkButton(
            main_frame,
            text="📄 Outro (Valor Fixo)",
            command=lambda: [dialog.destroy(), self.abrir_dialog_outro(secao_despesas.id)],
            height=40,
            fg_color="#FF9800",
            hover_color="#e68900"
        )
        btn_outro.pack(fill="x", pady=(0, 10))

        btn_cancelar = ctk.CTkButton(
            main_frame,
            text="Cancelar",
            command=dialog.destroy,
            height=35,
            fg_color="gray",
            hover_color="#5a5a5a"
        )
        btn_cancelar.pack(fill="x")

    def abrir_dialog_servico_cliente(self, secao_id: int):
        """Abre dialog para adicionar serviço"""
        dialog = ServicoDialogCliente(self, self.db_session, self.orcamento_id, secao_id)
        self.wait_window(dialog)
        if dialog.success:
            self.carregar_items_cliente()

    def abrir_dialog_equipamento_cliente(self, secao_id: int):
        """Abre dialog para adicionar equipamento"""
        dialog = EquipamentoDialogCliente(self, self.db_session, self.orcamento_id, secao_id)
        self.wait_window(dialog)
        if dialog.success:
            self.carregar_items_cliente()

    def abrir_dialog_transporte(self, secao_id: int, item_id: Optional[int] = None):
        """Abre dialog para adicionar transporte"""
        dialog = TransporteDialog(self, self.db_session, self.orcamento_id, secao_id, item_id)
        self.wait_window(dialog)
        if dialog.success:
            # Obter ID do item criado/atualizado
            if hasattr(dialog, 'item_created_id'):
                self.sincronizar_despesa_cliente_empresa(dialog.item_created_id)
            self.carregar_items_cliente()

    def abrir_dialog_refeicao(self, secao_id: int, item_id: Optional[int] = None):
        """Abre dialog para adicionar refeição"""
        dialog = RefeicaoDialog(self, self.db_session, self.orcamento_id, secao_id, item_id)
        self.wait_window(dialog)
        if dialog.success:
            if hasattr(dialog, 'item_created_id'):
                self.sincronizar_despesa_cliente_empresa(dialog.item_created_id)
            self.carregar_items_cliente()

    def abrir_dialog_outro(self, secao_id: int, item_id: Optional[int] = None):
        """Abre dialog para adicionar outro"""
        dialog = OutroDialog(self, self.db_session, self.orcamento_id, secao_id, item_id)
        self.wait_window(dialog)
        if dialog.success:
            if hasattr(dialog, 'item_created_id'):
                self.sincronizar_despesa_cliente_empresa(dialog.item_created_id)
            self.carregar_items_cliente()

    def carregar_items_cliente(self):
        """Carrega e renderiza todos os items do LADO CLIENTE"""
        if not self.orcamento_id:
            return

        # Limpar área
        for widget in self.cliente_scroll.winfo_children():
            widget.destroy()

        # Obter secções
        secoes = self.manager.obter_secoes(self.orcamento_id)

        # Organizar secções principais (Serviços, Equipamento, Despesas)
        secoes_principais = {
            'servicos': next((s for s in secoes if s.tipo == 'servicos'), None),
            'equipamento': next((s for s in secoes if s.tipo == 'equipamento'), None),
            'despesas': next((s for s in secoes if s.tipo == 'despesas'), None)
        }

        total_geral = Decimal('0')

        for nome_secao, secao_obj in secoes_principais.items():
            if not secao_obj:
                continue

            # Obter items desta secção
            items = self.manager.obter_itens(self.orcamento_id, secao_obj.id)
            if not items:
                continue  # Não mostrar secções vazias

            # Frame da secção
            secao_frame = ctk.CTkFrame(
                self.cliente_scroll,
                fg_color=("#f5f5f5", "#2b2b2b"),
                corner_radius=10
            )
            secao_frame.pack(fill="x", padx=10, pady=(0, 15))

            # Header da secção
            header_frame = ctk.CTkFrame(secao_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(15, 10))

            # Nome da secção
            nome_display = {
                'servicos': '🔧 SERVIÇOS',
                'equipamento': '📦 EQUIPAMENTO',
                'despesas': '💰 DESPESAS'
            }.get(nome_secao, nome_secao.upper())

            ctk.CTkLabel(
                header_frame,
                text=nome_display,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left")

            # Items da secção
            subtotal_secao = Decimal('0')
            for idx, item in enumerate(items):
                self.renderizar_item_cliente(secao_frame, item, idx)
                subtotal_secao += item.total

            # Subtotal da secção
            subtotal_frame = ctk.CTkFrame(secao_frame, fg_color="transparent")
            subtotal_frame.pack(fill="x", padx=15, pady=(5, 10))

            ctk.CTkLabel(
                subtotal_frame,
                text=f"Subtotal: €{float(subtotal_secao):.2f}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#2c3e50", "#ecf0f1")
            ).pack(side="right")

            total_geral += subtotal_secao

        # Atualizar total geral
        self._total_cliente = total_geral
        self.atualizar_total_cliente()

    def renderizar_item_cliente(self, parent, item: OrcamentoItem, index: int):
        """Renderiza um item CLIENTE"""
        # Cor de fundo alternada
        bg_color = ("#ffffff", "#1e1e1e") if index % 2 == 0 else ("#f9f9f9", "#252525")

        item_frame = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=6)
        item_frame.pack(fill="x", padx=15, pady=2)

        # Container principal (descrição + detalhes + ações)
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=8)

        # Coluna 1: Descrição + Tipo
        desc_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        desc_frame.pack(side="left", fill="both", expand=True)

        # Tipo badge
        tipo_colors = {
            'servico': ("#4CAF50", "#2e7d32"),
            'equipamento': ("#2196F3", "#1565c0"),
            'transporte': ("#FF9800", "#e65100"),
            'refeicao': ("#FF9800", "#e65100"),
            'outro': ("#FF9800", "#e65100")
        }
        tipo_bg = tipo_colors.get(item.tipo, ("#9E9E9E", "#616161"))

        ctk.CTkLabel(
            desc_frame,
            text=item.tipo.upper(),
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=tipo_bg,
            corner_radius=4,
            padx=6,
            pady=2
        ).pack(side="left", padx=(0, 8))

        # Descrição
        desc_text = item.descricao[:60] + "..." if len(item.descricao) > 60 else item.descricao
        ctk.CTkLabel(
            desc_frame,
            text=desc_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Coluna 2: Detalhes (campos específicos por tipo)
        details_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        details_frame.pack(side="left", padx=20)

        if item.tipo in ['servico', 'equipamento']:
            detail_text = f"{item.quantidade} × {item.dias}d × €{float(item.preco_unitario):.2f}"
            if item.desconto and item.desconto > 0:
                detail_text += f" (-{float(item.desconto * 100):.1f}%)"
        elif item.tipo == 'transporte':
            detail_text = f"{float(item.kms):.1f}km × €{float(item.valor_por_km):.2f}/km"
        elif item.tipo == 'refeicao':
            detail_text = f"{item.num_refeicoes} refeições × €{float(item.valor_por_refeicao):.2f}"
        elif item.tipo == 'outro':
            detail_text = f"Valor fixo"
        else:
            detail_text = ""

        ctk.CTkLabel(
            details_frame,
            text=detail_text,
            font=ctk.CTkFont(size=11),
            text_color=("#555", "#aaa")
        ).pack()

        # Coluna 3: Total
        total_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        total_frame.pack(side="left", padx=10)

        ctk.CTkLabel(
            total_frame,
            text=f"€{float(item.total):.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#2e7d32", "#66bb6a")
        ).pack()

        # Coluna 4: Ações (Edit/Delete)
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(side="right")

        btn_editar = ctk.CTkButton(
            actions_frame,
            text="✏️",
            command=lambda: self.editar_item_cliente(item),
            width=30,
            height=28,
            fg_color=("#2196F3", "#1565c0"),
            hover_color=("#1976D2", "#0d47a1")
        )
        btn_editar.pack(side="left", padx=2)

        btn_eliminar = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            command=lambda: self.eliminar_item_cliente(item.id),
            width=30,
            height=28,
            fg_color=("#f44336", "#c62828"),
            hover_color=("#d32f2f", "#b71c1c")
        )
        btn_eliminar.pack(side="left", padx=2)

    def editar_item_cliente(self, item: OrcamentoItem):
        """Abre dialog para editar item CLIENTE"""
        # Determinar qual dialog abrir baseado no tipo
        if item.tipo == 'servico':
            dialog = ServicoDialogCliente(self, self.db_session, self.orcamento_id, item.secao_id, item.id)
        elif item.tipo == 'equipamento':
            dialog = EquipamentoDialogCliente(self, self.db_session, self.orcamento_id, item.secao_id, item.id)
        elif item.tipo == 'transporte':
            dialog = TransporteDialog(self, self.db_session, self.orcamento_id, item.secao_id, item.id)
        elif item.tipo == 'refeicao':
            dialog = RefeicaoDialog(self, self.db_session, self.orcamento_id, item.secao_id, item.id)
        elif item.tipo == 'outro':
            dialog = OutroDialog(self, self.db_session, self.orcamento_id, item.secao_id, item.id)
        else:
            messagebox.showerror("Erro", f"Tipo de item desconhecido: {item.tipo}")
            return

        self.wait_window(dialog)
        if dialog.success:
            self.carregar_items_cliente()

    def eliminar_item_cliente(self, item_id: int):
        """Elimina item CLIENTE"""
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja eliminar este item?"):
            return

        # Verificar se é despesa (tem que eliminar espelhada também)
        item = self.db_session.query(OrcamentoItem).filter(OrcamentoItem.id == item_id).first()
        if item and item.tipo in ['transporte', 'refeicao', 'outro']:
            # Eliminar despesa espelhada primeiro
            rep_espelhada = self.db_session.query(OrcamentoReparticao).filter(
                OrcamentoReparticao.item_cliente_id == item_id
            ).first()
            if rep_espelhada:
                self.manager.eliminar_reparticao(rep_espelhada.id)

        sucesso, erro = self.manager.eliminar_item(item_id)
        if sucesso:
            self.carregar_items_cliente()
            # Recarregar lado EMPRESA também (para remover espelhada)
            self.carregar_items_empresa()
        else:
            messagebox.showerror("Erro", f"Erro ao eliminar: {erro}")

    def sincronizar_despesa_cliente_empresa(self, item_cliente_id: int):
        """
        Sincroniza despesa CLIENTE→EMPRESA automaticamente
        Cria ou atualiza despesa espelhada no lado EMPRESA
        """
        # Obter item CLIENTE
        item_cliente = self.db_session.query(OrcamentoItem).filter(
            OrcamentoItem.id == item_cliente_id
        ).first()

        if not item_cliente or item_cliente.tipo not in ['transporte', 'refeicao', 'outro']:
            return  # Não é despesa, não sincroniza

        # Verificar se já existe despesa espelhada
        rep_espelhada = self.db_session.query(OrcamentoReparticao).filter(
            OrcamentoReparticao.item_cliente_id == item_cliente_id
        ).first()

        if rep_espelhada:
            # Atualizar existente
            rep_espelhada.descricao = item_cliente.descricao
            rep_espelhada.beneficiario = "AGORA"  # Sempre AGORA
            rep_espelhada.tipo = 'despesa'

            # Copiar campos específicos
            rep_espelhada.kms = item_cliente.kms
            rep_espelhada.valor_por_km = item_cliente.valor_por_km
            rep_espelhada.num_refeicoes = item_cliente.num_refeicoes
            rep_espelhada.valor_por_refeicao = item_cliente.valor_por_refeicao
            rep_espelhada.valor_fixo = item_cliente.valor_fixo

            # Recalcular total
            rep_espelhada.total = rep_espelhada.calcular_total()
            self.db_session.commit()
        else:
            # Criar nova despesa espelhada
            rep_espelhada = OrcamentoReparticao(
                orcamento_id=self.orcamento_id,
                tipo='despesa',
                beneficiario='AGORA',
                descricao=item_cliente.descricao,
                kms=item_cliente.kms,
                valor_por_km=item_cliente.valor_por_km,
                num_refeicoes=item_cliente.num_refeicoes,
                valor_por_refeicao=item_cliente.valor_por_refeicao,
                valor_fixo=item_cliente.valor_fixo,
                item_cliente_id=item_cliente_id,
                total=Decimal('0')
            )
            rep_espelhada.total = rep_espelhada.calcular_total()
            self.db_session.add(rep_espelhada)
            self.db_session.commit()

        # Recarregar lado EMPRESA para mostrar sincronização
        self.carregar_items_empresa()

    def atualizar_total_cliente(self):
        """Atualiza TOTAL CLIENTE"""
        # _total_cliente já foi calculado em carregar_items_cliente()
        self.total_cliente_label.configure(text=f"TOTAL CLIENTE: €{float(self._total_cliente):.2f}")

        # Validar contra TOTAL EMPRESA
        self.validar_totais()

    # ========================================
    # MÉTODOS DE NEGÓCIO - TAB EMPRESA
    # ========================================

    def adicionar_item_empresa(self, tipo):
        """Abre dialog para adicionar item no lado EMPRESA"""
        if not self.orcamento_id:
            messagebox.showwarning("Aviso", "Grave o orçamento antes de adicionar items!")
            return

        if tipo == 'servico':
            dialog = ServicoDialogEmpresa(self, self.db_session, self.orcamento_id)
            self.wait_window(dialog)
            if dialog.success:
                self.carregar_items_empresa()

        elif tipo == 'equipamento':
            dialog = EquipamentoDialogEmpresa(self, self.db_session, self.orcamento_id)
            self.wait_window(dialog)
            if dialog.success:
                self.carregar_items_empresa()

    def auto_preencher_comissoes(self):
        """Auto-preenche comissões com valores padrão"""
        if not self.orcamento_id:
            messagebox.showwarning("Aviso", "Grave o orçamento primeiro!")
            return

        # Calcular base de cálculo (TOTAL CLIENTE)
        base_calculo = self._total_cliente

        if base_calculo <= 0:
            messagebox.showwarning(
                "Aviso",
                "Não há valores no lado CLIENTE para calcular comissões!\n"
                "Adicione serviços ou equipamento primeiro."
            )
            return

        # Verificar se já existem comissões
        reparticoes_existentes = self.manager.obter_reparticoes(self.orcamento_id)
        comissoes_existentes = [r for r in reparticoes_existentes if r.tipo == 'comissao']

        if comissoes_existentes:
            if not messagebox.askyesno(
                "Aviso",
                f"Já existem {len(comissoes_existentes)} comissão(ões) criada(s).\n"
                "Deseja eliminar as existentes e criar novas com valores padrão?"
            ):
                return

            # Eliminar comissões existentes
            for comissao in comissoes_existentes:
                self.manager.eliminar_reparticao(comissao.id)

        # Obter owner do orçamento (para comissão de venda)
        orcamento = self.manager.obter_orcamento(self.orcamento_id)
        owner = orcamento.owner if orcamento else "BA"

        # 1. Criar Comissão de Venda (5% para owner)
        comissao_venda = OrcamentoReparticao(
            orcamento_id=self.orcamento_id,
            tipo='comissao',
            beneficiario=owner,
            descricao=f"Comissão de Venda ({owner})",
            percentagem=Decimal('5.000'),  # 5%
            base_calculo=base_calculo,
            total=Decimal('0')
        )
        comissao_venda.total = comissao_venda.calcular_total()
        self.db_session.add(comissao_venda)

        # 2. Criar Comissão Empresa (10% para AGORA)
        comissao_empresa = OrcamentoReparticao(
            orcamento_id=self.orcamento_id,
            tipo='comissao',
            beneficiario='AGORA',
            descricao="Comissão Empresa (AGORA)",
            percentagem=Decimal('10.000'),  # 10%
            base_calculo=base_calculo,
            total=Decimal('0')
        )
        comissao_empresa.total = comissao_empresa.calcular_total()
        self.db_session.add(comissao_empresa)

        self.db_session.commit()

        # Recarregar lado EMPRESA
        self.carregar_items_empresa()

        messagebox.showinfo(
            "Sucesso",
            f"Comissões criadas com sucesso!\n\n"
            f"Base de cálculo: €{float(base_calculo):.2f}\n"
            f"• Comissão Venda ({owner}): 5% = €{float(comissao_venda.total):.2f}\n"
            f"• Comissão Empresa (AGORA): 10% = €{float(comissao_empresa.total):.2f}\n\n"
            f"Pode editar as percentagens clicando no botão ✏️"
        )

    def carregar_items_empresa(self):
        """Carrega e renderiza todos os items do LADO EMPRESA"""
        if not self.orcamento_id:
            return

        # Limpar área
        for widget in self.empresa_scroll.winfo_children():
            widget.destroy()

        # Obter repartições (items EMPRESA)
        reparticoes = self.manager.obter_reparticoes(self.orcamento_id)

        if not reparticoes:
            # Mostrar mensagem se vazio
            empty_label = ctk.CTkLabel(
                self.empresa_scroll,
                text="Nenhum item EMPRESA adicionado ainda.\nUse os botões acima para adicionar.",
                font=ctk.CTkFont(size=12),
                text_color=("#999", "#666")
            )
            empty_label.pack(pady=40)
            self.atualizar_total_empresa()
            return

        # Agrupar por tipo
        grupos = {
            'servico': [],
            'equipamento': [],
            'despesa': [],
            'comissao': []
        }

        for rep in reparticoes:
            grupos[rep.tipo].append(rep)

        total_geral = Decimal('0')

        # Renderizar grupos
        grupos_display = {
            'servico': ('🔧 SERVIÇOS', "#4CAF50"),
            'equipamento': ('📦 EQUIPAMENTO', "#2196F3"),
            'despesa': ('💰 DESPESAS ESPELHADAS', "#FF9800"),
            'comissao': ('💼 COMISSÕES', "#9C27B0")
        }

        for tipo, items_grupo in grupos.items():
            if not items_grupo:
                continue

            nome_grupo, cor_grupo = grupos_display[tipo]

            # Frame do grupo
            grupo_frame = ctk.CTkFrame(
                self.empresa_scroll,
                fg_color=("#f5f5f5", "#2b2b2b"),
                corner_radius=10
            )
            grupo_frame.pack(fill="x", padx=10, pady=(0, 15))

            # Header do grupo
            header_frame = ctk.CTkFrame(grupo_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(15, 10))

            ctk.CTkLabel(
                header_frame,
                text=nome_grupo,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left")

            # Items do grupo
            subtotal_grupo = Decimal('0')
            for idx, rep in enumerate(items_grupo):
                self.renderizar_item_empresa(grupo_frame, rep, idx, tipo)
                subtotal_grupo += rep.total

            # Subtotal do grupo
            subtotal_frame = ctk.CTkFrame(grupo_frame, fg_color="transparent")
            subtotal_frame.pack(fill="x", padx=15, pady=(5, 10))

            ctk.CTkLabel(
                subtotal_frame,
                text=f"Subtotal: €{float(subtotal_grupo):.2f}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#2c3e50", "#ecf0f1")
            ).pack(side="right")

            total_geral += subtotal_grupo

        # Atualizar total geral
        self._total_empresa = total_geral
        self.atualizar_total_empresa()

    def renderizar_item_empresa(self, parent, rep: OrcamentoReparticao, index: int, tipo: str):
        """Renderiza um item EMPRESA"""
        # Cor de fundo alternada
        bg_color = ("#ffffff", "#1e1e1e") if index % 2 == 0 else ("#f9f9f9", "#252525")

        # Se for despesa espelhada, usar cor diferente (readonly)
        is_espelhada = (tipo == 'despesa')
        if is_espelhada:
            bg_color = ("#fff8e1", "#3e2723")

        item_frame = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=6)
        item_frame.pack(fill="x", padx=15, pady=2)

        # Container principal
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=8)

        # Coluna 1: Beneficiário badge + Descrição
        desc_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        desc_frame.pack(side="left", fill="both", expand=True)

        # Beneficiário badge
        beneficiario_colors = {
            'BA': ("#4CAF50", "#2e7d32"),
            'RR': ("#2196F3", "#1565c0"),
            'AGORA': ("#9C27B0", "#6a1b9a")
        }
        benef_bg = beneficiario_colors.get(rep.beneficiario, ("#9E9E9E", "#616161"))

        benef_text = rep.beneficiario if rep.beneficiario else "N/A"
        if is_espelhada:
            benef_text = "🔗 AGORA"  # Despesas sempre vão para AGORA

        ctk.CTkLabel(
            desc_frame,
            text=benef_text,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=benef_bg,
            corner_radius=4,
            padx=6,
            pady=2
        ).pack(side="left", padx=(0, 8))

        # Descrição
        desc_text = rep.descricao[:50] + "..." if len(rep.descricao) > 50 else rep.descricao
        if is_espelhada:
            desc_text = "🔗 " + desc_text  # Indicador visual de espelhado

        ctk.CTkLabel(
            desc_frame,
            text=desc_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Coluna 2: Detalhes
        details_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        details_frame.pack(side="left", padx=20)

        if tipo in ['servico', 'equipamento']:
            detail_text = f"{rep.quantidade} × {rep.dias}d × €{float(rep.valor_unitario):.2f}"
        elif tipo == 'comissao':
            detail_text = f"{float(rep.percentagem):.3f}% × €{float(rep.base_calculo):.2f}"
        elif tipo == 'despesa':
            # Despesas espelhadas - mostrar detalhes do tipo
            if rep.kms:
                detail_text = f"{float(rep.kms):.1f}km × €{float(rep.valor_por_km):.2f}/km"
            elif rep.num_refeicoes:
                detail_text = f"{rep.num_refeicoes} ref. × €{float(rep.valor_por_refeicao):.2f}"
            elif rep.valor_fixo:
                detail_text = "Valor fixo"
            else:
                detail_text = "Espelhado"
        else:
            detail_text = ""

        ctk.CTkLabel(
            details_frame,
            text=detail_text,
            font=ctk.CTkFont(size=11),
            text_color=("#555", "#aaa")
        ).pack()

        # Coluna 3: Total
        total_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        total_frame.pack(side="left", padx=10)

        ctk.CTkLabel(
            total_frame,
            text=f"€{float(rep.total):.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#2e7d32", "#66bb6a")
        ).pack()

        # Coluna 4: Ações
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(side="right")

        if not is_espelhada:
            # Edit/Delete buttons (apenas para items não-espelhados)
            btn_editar = ctk.CTkButton(
                actions_frame,
                text="✏️",
                command=lambda: self.editar_item_empresa(rep),
                width=30,
                height=28,
                fg_color=("#2196F3", "#1565c0"),
                hover_color=("#1976D2", "#0d47a1")
            )
            btn_editar.pack(side="left", padx=2)

            btn_eliminar = ctk.CTkButton(
                actions_frame,
                text="🗑️",
                command=lambda: self.eliminar_item_empresa(rep.id),
                width=30,
                height=28,
                fg_color=("#f44336", "#c62828"),
                hover_color=("#d32f2f", "#b71c1c")
            )
            btn_eliminar.pack(side="left", padx=2)
        else:
            # Readonly indicator
            ctk.CTkLabel(
                actions_frame,
                text="🔒 READONLY",
                font=ctk.CTkFont(size=9),
                text_color=("#999", "#666")
            ).pack()

    def editar_item_empresa(self, rep: OrcamentoReparticao):
        """Abre dialog para editar item EMPRESA"""
        if rep.tipo == 'servico':
            dialog = ServicoDialogEmpresa(self, self.db_session, self.orcamento_id, rep.id)
        elif rep.tipo == 'equipamento':
            dialog = EquipamentoDialogEmpresa(self, self.db_session, self.orcamento_id, rep.id)
        elif rep.tipo == 'comissao':
            # Passar base de cálculo atual
            dialog = ComissaoDialog(self, self.db_session, self.orcamento_id, rep.base_calculo or Decimal('0'), rep.id)
        else:
            messagebox.showerror("Erro", f"Tipo de item EMPRESA desconhecido: {rep.tipo}")
            return

        self.wait_window(dialog)
        if dialog.success:
            self.carregar_items_empresa()

    def eliminar_item_empresa(self, rep_id: int):
        """Elimina item EMPRESA"""
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja eliminar este item?"):
            return

        sucesso, erro = self.manager.eliminar_reparticao(rep_id)
        if sucesso:
            self.carregar_items_empresa()
        else:
            messagebox.showerror("Erro", f"Erro ao eliminar: {erro}")

    def atualizar_total_empresa(self):
        """Atualiza TOTAL EMPRESA"""
        # _total_empresa já foi calculado em carregar_items_empresa()
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
# DIALOGS ESPECÍFICOS POR TIPO - LADO CLIENTE
# ========================================

# ServicoDialog and EquipamentoDialog are now imported from ui.dialogs - create aliases for compatibility
ServicoDialogCliente = ServicoDialog
EquipamentoDialogCliente = EquipamentoDialog


# TransporteDialog, RefeicaoDialog, and OutroDialog are now imported from ui.dialogs


# ========================================
# DIALOGS ESPECÍFICOS POR TIPO - LADO EMPRESA
# ========================================

# ServicoEmpresaDialog and EquipamentoEmpresaDialog are now imported from ui.dialogs


# ComissaoDialog is now imported from ui.dialogs

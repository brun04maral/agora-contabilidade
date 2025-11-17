# -*- coding: utf-8 -*-
"""
Tela de Formulário de Orçamento - Criar/Editar Orçamento
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.orcamentos import OrcamentoManager
from logic.clientes import ClientesManager
from ui.components.autocomplete_entry import AutocompleteEntry
from ui.components.date_picker_dropdown import DatePickerDropdown
from ui.dialogs.servico_empresa_dialog import ServicoEmpresaDialog
from ui.dialogs.equipamento_empresa_dialog import EquipamentoEmpresaDialog
from ui.dialogs.despesa_dialog import DespesaDialog
from ui.dialogs.comissao_dialog import ComissaoDialog
from ui.dialogs.aluguer_equipamento_dialog import AluguerEquipamentoDialog
from ui.dialogs.outro_empresa_dialog import OutroEmpresaDialog
from database.models.orcamento import OrcamentoItem, OrcamentoSecao
from typing import Optional
from datetime import date
from tkinter import messagebox
import tkinter as tk


class OrcamentoFormScreen(ctk.CTkFrame):
    """
    Screen para criar/editar orçamentos
    Implementa estrutura base com tabs Cliente/Empresa
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
        self.secao_empresa_id = None  # ID da secção EMPRESA (será criada quando necessário)

        # Configure
        self.configure(fg_color="transparent")

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
        # 1. HEADER com botão voltar
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Botão voltar
        voltar_btn = ctk.CTkButton(
            header_frame,
            text="⬅️ Voltar",
            command=self.voltar,
            width=100,
            height=35
        )
        voltar_btn.pack(side="left", padx=(0, 20))

        # Título
        titulo = "Novo Orçamento" if not self.orcamento_id else f"Editar Orçamento"
        title_label = ctk.CTkLabel(
            header_frame,
            text=titulo,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")

        # 2. CAMPOS DO ORÇAMENTO
        fields_frame = ctk.CTkFrame(self)
        fields_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Grid layout para campos
        fields_frame.columnconfigure(0, weight=0)  # Labels
        fields_frame.columnconfigure(1, weight=1)  # Fields
        fields_frame.columnconfigure(2, weight=0)  # Labels
        fields_frame.columnconfigure(3, weight=1)  # Fields

        # Row 0: Código | Owner
        # Código (readonly)
        ctk.CTkLabel(fields_frame, text="Código:").grid(
            row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="w"
        )
        self.codigo_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Gerado automaticamente...",
            state="disabled"
        )
        self.codigo_entry.grid(row=0, column=1, padx=(0, 20), pady=(20, 10), sticky="ew")

        # Owner (BA/RR)
        ctk.CTkLabel(fields_frame, text="Owner: *").grid(
            row=0, column=2, padx=(20, 10), pady=(20, 10), sticky="w"
        )
        self.owner_dropdown = ctk.CTkComboBox(
            fields_frame,
            values=["BA", "RR"],
            state="readonly"
        )
        self.owner_dropdown.set("BA")
        self.owner_dropdown.grid(row=0, column=3, padx=(0, 20), pady=(20, 10), sticky="ew")

        # Row 1: Cliente | Estado
        ctk.CTkLabel(fields_frame, text="Cliente: *").grid(
            row=1, column=0, padx=(20, 10), pady=(0, 10), sticky="w"
        )

        # Autocomplete para Cliente
        clientes = self.clientes_manager.listar_todos()
        cliente_names = [f"{c.numero} - {c.nome}" for c in clientes]
        self.clientes_map = {f"{c.numero} - {c.nome}": c.id for c in clientes}

        self.cliente_autocomplete = AutocompleteEntry(
            fields_frame,
            options=cliente_names,
            placeholder="Começar a escrever o nome do cliente..."
        )
        self.cliente_autocomplete.grid(row=1, column=1, padx=(0, 20), pady=(0, 10), sticky="ew")

        # Estado (badge readonly)
        ctk.CTkLabel(fields_frame, text="Estado:").grid(
            row=1, column=2, padx=(20, 10), pady=(0, 10), sticky="w"
        )
        self.estado_label = ctk.CTkLabel(
            fields_frame,
            text="RASCUNHO",
            fg_color="gray",
            corner_radius=6,
            padx=15,
            pady=5
        )
        self.estado_label.grid(row=1, column=3, padx=(0, 20), pady=(0, 10), sticky="w")

        # Row 2: Data Criação | Data Evento
        ctk.CTkLabel(fields_frame, text="Data Criação: *").grid(
            row=2, column=0, padx=(20, 10), pady=(0, 10), sticky="w"
        )
        self.data_criacao_picker = DatePickerDropdown(
            fields_frame,
            default_date=date.today()
        )
        self.data_criacao_picker.grid(row=2, column=1, padx=(0, 20), pady=(0, 10), sticky="ew")

        ctk.CTkLabel(fields_frame, text="Data Evento:").grid(
            row=2, column=2, padx=(20, 10), pady=(0, 10), sticky="w"
        )
        self.data_evento_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ex: 15-20/11/2025"
        )
        self.data_evento_entry.grid(row=2, column=3, padx=(0, 20), pady=(0, 10), sticky="ew")

        # Row 3: Local Evento
        ctk.CTkLabel(fields_frame, text="Local Evento:").grid(
            row=3, column=0, padx=(20, 10), pady=(0, 20), sticky="w"
        )
        self.local_evento_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Local do evento..."
        )
        self.local_evento_entry.grid(row=3, column=1, columnspan=3, padx=(0, 20), pady=(0, 20), sticky="ew")

        # 3. TABS Cliente/Empresa
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Tab Cliente (placeholder)
        self.tab_cliente = self.tabview.add("👤 CLIENTE")
        placeholder_cliente = ctk.CTkLabel(
            self.tab_cliente,
            text="📑 Secções e Items CLIENTE serão implementados em fase futura",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        placeholder_cliente.pack(expand=True)

        # Total Cliente
        total_cliente_frame = ctk.CTkFrame(self.tab_cliente)
        total_cliente_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        self.total_cliente_label = ctk.CTkLabel(
            total_cliente_frame,
            text="TOTAL CLIENTE: €0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        self.total_cliente_label.pack(pady=10)

        # Tab Empresa (implementação completa)
        self.tab_empresa = self.tabview.add("🏢 EMPRESA")
        self.create_empresa_tab()

        # 4. FOOTER com botões
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=30, pady=(0, 30))

        # Botão Gravar
        self.gravar_btn = ctk.CTkButton(
            footer_frame,
            text="💾 Gravar Rascunho",
            command=self.gravar_rascunho,
            width=150,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.gravar_btn.pack(side="left", padx=(0, 10))

        # Botão Aprovar (condicional)
        self.aprovar_btn = ctk.CTkButton(
            footer_frame,
            text="✓ Aprovar",
            command=self.aprovar,
            width=120,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )

        # Botão Anular (condicional)
        self.anular_btn = ctk.CTkButton(
            footer_frame,
            text="❌ Anular",
            command=self.anular,
            width=120,
            height=35,
            fg_color="#f44336",
            hover_color="#da190b"
        )

        # Atualizar botões baseado no estado
        self.atualizar_botoes_acao()

    def create_empresa_tab(self):
        """Cria conteúdo da tab EMPRESA"""
        # Container principal
        main_container = ctk.CTkScrollableFrame(self.tab_empresa)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header da secção
        header_label = ctk.CTkLabel(
            main_container,
            text="💼 Items EMPRESA - Repartição Interna",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(anchor="w", pady=(0, 10))

        info_label = ctk.CTkLabel(
            main_container,
            text="Adicione items da parte económica interna (não visível ao cliente)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(anchor="w", pady=(0, 15))

        # Botões para adicionar items (6 botões em 2 rows)
        buttons_frame = ctk.CTkFrame(main_container)
        buttons_frame.pack(fill="x", pady=(0, 15))

        # Row 1: Serviço, Equipamento, Despesa
        row1 = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 5))

        ctk.CTkButton(
            row1,
            text="➕ Serviço",
            command=self.adicionar_servico_empresa,
            width=180,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            row1,
            text="➕ Equipamento",
            command=self.adicionar_equipamento_empresa,
            width=180,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            row1,
            text="➕ Despesa (Espelhar)",
            command=self.adicionar_despesa_espelhamento,
            width=180,
            height=35,
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="left", padx=(0, 10))

        # Row 2: Comissão, Aluguer Equip., Outro
        row2 = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        row2.pack(fill="x")

        ctk.CTkButton(
            row2,
            text="➕ Comissão",
            command=self.adicionar_comissao,
            width=180,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            row2,
            text="➕ Aluguer Equip.",
            command=self.adicionar_aluguer_equipamento,
            width=180,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            row2,
            text="➕ Outro",
            command=self.adicionar_outro_empresa,
            width=180,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="left", padx=(0, 10))

        # Tabela de items EMPRESA
        table_label = ctk.CTkLabel(
            main_container,
            text="Items Adicionados:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        table_label.pack(anchor="w", pady=(15, 10))

        # Frame para tabela com scrollbar
        self.items_empresa_frame = ctk.CTkFrame(main_container)
        self.items_empresa_frame.pack(fill="both", expand=True)

        # Header da tabela
        header_table_frame = ctk.CTkFrame(self.items_empresa_frame, fg_color="#2b2b2b")
        header_table_frame.pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(header_table_frame, text="Descrição", width=250, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_table_frame, text="Beneficiário", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_table_frame, text="Qtd", width=60, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_table_frame, text="Valor Unit.", width=90, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_table_frame, text="Total", width=90, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(header_table_frame, text="Ações", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)

        # Container para rows (scrollable)
        self.items_rows_frame = ctk.CTkScrollableFrame(self.items_empresa_frame, height=200)
        self.items_rows_frame.pack(fill="both", expand=True)

        # Placeholder quando vazio
        self.empty_label = ctk.CTkLabel(
            self.items_rows_frame,
            text="Nenhum item adicionado. Use os botões acima para adicionar.",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        )
        self.empty_label.pack(pady=30)

        # Total Empresa (rodapé)
        total_empresa_frame = ctk.CTkFrame(self.tab_empresa)
        total_empresa_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        # Comparação de totais
        self.comparacao_frame = ctk.CTkFrame(total_empresa_frame, fg_color="transparent")
        self.comparacao_frame.pack(pady=(0, 10))

        self.comparacao_label = ctk.CTkLabel(
            self.comparacao_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.comparacao_label.pack()

        # Total
        self.total_empresa_label = ctk.CTkLabel(
            total_empresa_frame,
            text="TOTAL EMPRESA: €0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        self.total_empresa_label.pack(pady=10)

    def obter_ou_criar_secao_empresa(self):
        """Obtém ou cria secção EMPRESA"""
        if not self.orcamento_id:
            messagebox.showwarning("Aviso", "Por favor, grave o orçamento primeiro antes de adicionar items.")
            return None

        # Verificar se já existe secção EMPRESA
        secao = self.db_session.query(OrcamentoSecao).filter(
            OrcamentoSecao.orcamento_id == self.orcamento_id,
            OrcamentoSecao.tipo == "empresa"
        ).first()

        if not secao:
            # Criar nova secção
            secao = OrcamentoSecao(
                orcamento_id=self.orcamento_id,
                tipo="empresa",
                nome="Items EMPRESA",
                ordem=999  # Última secção
            )
            self.db_session.add(secao)
            self.db_session.commit()

        self.secao_empresa_id = secao.id
        return secao.id

    def adicionar_servico_empresa(self):
        """Abre dialog para adicionar serviço EMPRESA"""
        secao_id = self.obter_ou_criar_secao_empresa()
        if not secao_id:
            return

        dialog = ServicoEmpresaDialog(
            self,
            self.db_session,
            self.orcamento_id,
            secao_id
        )
        dialog.wait_window()
        self.carregar_items_empresa()

    def adicionar_equipamento_empresa(self):
        """Abre dialog para adicionar equipamento EMPRESA"""
        secao_id = self.obter_ou_criar_secao_empresa()
        if not secao_id:
            return

        dialog = EquipamentoEmpresaDialog(
            self,
            self.db_session,
            self.orcamento_id,
            secao_id
        )
        dialog.wait_window()
        self.carregar_items_empresa()

    def adicionar_despesa_espelhamento(self):
        """Abre dialog para espelhar despesas CLIENTE→EMPRESA"""
        secao_id = self.obter_ou_criar_secao_empresa()
        if not secao_id:
            return

        dialog = DespesaDialog(
            self,
            self.db_session,
            self.orcamento_id,
            secao_id
        )
        dialog.wait_window()
        self.carregar_items_empresa()

    def adicionar_comissao(self):
        """Abre dialog para adicionar comissão"""
        secao_id = self.obter_ou_criar_secao_empresa()
        if not secao_id:
            return

        dialog = ComissaoDialog(
            self,
            self.db_session,
            self.orcamento_id,
            secao_id
        )
        dialog.wait_window()
        self.carregar_items_empresa()

    def adicionar_aluguer_equipamento(self):
        """Abre dialog para adicionar aluguer de equipamento"""
        secao_id = self.obter_ou_criar_secao_empresa()
        if not secao_id:
            return

        dialog = AluguerEquipamentoDialog(
            self,
            self.db_session,
            self.orcamento_id,
            secao_id
        )
        dialog.wait_window()
        self.carregar_items_empresa()

    def adicionar_outro_empresa(self):
        """Abre dialog para adicionar item genérico EMPRESA"""
        secao_id = self.obter_ou_criar_secao_empresa()
        if not secao_id:
            return

        dialog = OutroEmpresaDialog(
            self,
            self.db_session,
            self.orcamento_id,
            secao_id
        )
        dialog.wait_window()
        self.carregar_items_empresa()

    def carregar_items_empresa(self):
        """Carrega e exibe items EMPRESA na tabela"""
        # Limpar rows existentes
        for widget in self.items_rows_frame.winfo_children():
            widget.destroy()

        if not self.orcamento_id:
            self.empty_label = ctk.CTkLabel(
                self.items_rows_frame,
                text="Grave o orçamento primeiro para adicionar items.",
                text_color="gray",
                font=ctk.CTkFont(size=12)
            )
            self.empty_label.pack(pady=30)
            return

        # Buscar items EMPRESA
        items = self.db_session.query(OrcamentoItem).filter(
            OrcamentoItem.orcamento_id == self.orcamento_id
        ).order_by(OrcamentoItem.ordem).all()

        if not items:
            self.empty_label = ctk.CTkLabel(
                self.items_rows_frame,
                text="Nenhum item adicionado. Use os botões acima para adicionar.",
                text_color="gray",
                font=ctk.CTkFont(size=12)
            )
            self.empty_label.pack(pady=30)
            self.calcular_e_comparar_totais()
            return

        # Criar row para cada item
        for item in items:
            self.criar_row_item(item)

        # Calcular e exibir totais
        self.calcular_e_comparar_totais()

    def criar_row_item(self, item: OrcamentoItem):
        """Cria uma row na tabela para um item"""
        row_frame = ctk.CTkFrame(self.items_rows_frame, fg_color="#3b3b3b")
        row_frame.pack(fill="x", pady=1)

        # Descrição (truncada)
        descricao_truncada = item.descricao[:35] + "..." if len(item.descricao) > 35 else item.descricao
        ctk.CTkLabel(row_frame, text=descricao_truncada, width=250, anchor="w").pack(side="left", padx=5, pady=5)

        # Beneficiário
        beneficiario = item.afetacao or "N/A"
        ctk.CTkLabel(row_frame, text=beneficiario, width=100).pack(side="left", padx=5, pady=5)

        # Quantidade
        ctk.CTkLabel(row_frame, text=str(item.quantidade), width=60).pack(side="left", padx=5, pady=5)

        # Valor Unitário
        ctk.CTkLabel(row_frame, text=f"{float(item.preco_unitario):.2f}€", width=90).pack(side="left", padx=5, pady=5)

        # Total
        ctk.CTkLabel(row_frame, text=f"{float(item.total):.2f}€", width=90, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5, pady=5)

        # Ações
        acoes_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        acoes_frame.pack(side="left", padx=5)

        ctk.CTkButton(
            acoes_frame,
            text="✏️",
            command=lambda i=item: self.editar_item(i),
            width=40,
            height=25,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            acoes_frame,
            text="🗑️",
            command=lambda i=item: self.apagar_item(i),
            width=40,
            height=25,
            fg_color="#f44336",
            hover_color="#da190b"
        ).pack(side="left", padx=2)

        # Context menu (right-click)
        row_frame.bind("<Button-3>", lambda e, i=item: self.show_context_menu(e, i))  # Linux/Windows
        row_frame.bind("<Button-2>", lambda e, i=item: self.show_context_menu(e, i))  # Mac

    def editar_item(self, item: OrcamentoItem):
        """Edita um item EMPRESA"""
        # TODO: Determinar tipo de dialog baseado em campos do item
        # Por agora, abrir dialog genérico
        dialog = OutroEmpresaDialog(
            self,
            self.db_session,
            self.orcamento_id,
            item.secao_id,
            item=item
        )
        dialog.wait_window()
        self.carregar_items_empresa()

    def apagar_item(self, item: OrcamentoItem):
        """Apaga um item EMPRESA"""
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja apagar este item?"):
            return

        try:
            self.db_session.delete(item)
            self.db_session.commit()
            messagebox.showinfo("Sucesso", "Item apagado com sucesso!")
            self.carregar_items_empresa()
        except Exception as e:
            self.db_session.rollback()
            messagebox.showerror("Erro", f"Erro ao apagar item: {str(e)}")

    def show_context_menu(self, event, item: OrcamentoItem):
        """Mostra context menu (right-click) para item"""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏️ Editar", command=lambda: self.editar_item(item))
        menu.add_separator()
        menu.add_command(label="🗑️ Apagar", command=lambda: self.apagar_item(item))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def calcular_e_comparar_totais(self):
        """Calcula totais e compara CLIENTE vs EMPRESA"""
        if not self.orcamento_id:
            return

        # Total CLIENTE (placeholder - implementar quando tiver items cliente)
        total_cliente = 0.00

        # Total EMPRESA
        items_empresa = self.db_session.query(OrcamentoItem).filter(
            OrcamentoItem.orcamento_id == self.orcamento_id
        ).all()

        total_empresa = sum(float(item.total) for item in items_empresa)

        # Atualizar labels
        self.total_empresa_label.configure(text=f"TOTAL EMPRESA: €{total_empresa:.2f}")

        # Comparação
        diferenca = abs(total_cliente - total_empresa)

        if diferenca <= 0.01:  # Considerado igual (tolerância de 1 cêntimo)
            self.comparacao_label.configure(
                text="✅ Totais CLIENTE e EMPRESA coincidem",
                text_color="#4CAF50"
            )
        else:
            self.comparacao_label.configure(
                text=f"⚠️ Diferença: €{diferenca:.2f} (CLIENTE: €{total_cliente:.2f} | EMPRESA: €{total_empresa:.2f})",
                text_color="#FF9800"
            )

    def carregar_orcamento(self):
        """Carrega dados do orçamento para edição"""
        self.orcamento = self.manager.obter_orcamento(self.orcamento_id)
        if not self.orcamento:
            messagebox.showerror("Erro", "Orçamento não encontrado!")
            self.voltar()
            return

        # Preencher campos com dados
        self.codigo_entry.configure(state="normal")
        self.codigo_entry.delete(0, "end")
        self.codigo_entry.insert(0, self.orcamento.codigo)
        self.codigo_entry.configure(state="disabled")

        # Cliente
        if self.orcamento.cliente:
            cliente_key = f"{self.orcamento.cliente.numero} - {self.orcamento.cliente.nome}"
            self.cliente_autocomplete.set_value(cliente_key)

        # Data Criação
        if self.orcamento.data_criacao:
            self.data_criacao_picker.set_date(self.orcamento.data_criacao)

        # Data Evento
        if self.orcamento.data_evento:
            self.data_evento_entry.delete(0, "end")
            self.data_evento_entry.insert(0, self.orcamento.data_evento)

        # Local Evento
        if self.orcamento.local_evento:
            self.local_evento_entry.delete(0, "end")
            self.local_evento_entry.insert(0, self.orcamento.local_evento)

        # Atualizar estado badge
        self.atualizar_estado_badge()

        # Carregar items EMPRESA
        self.carregar_items_empresa()

        # Atualizar botões
        self.atualizar_botoes_acao()

        # Reset flag
        self.alteracoes_pendentes = False

    def atualizar_estado_badge(self):
        """Atualiza badge de estado"""
        if not self.orcamento:
            return

        estado = self.orcamento.status
        estado_texto = estado.upper()

        # Cores baseadas no estado
        cores = {
            "rascunho": "gray",
            "enviado": "#2196F3",  # Azul
            "aprovado": "#4CAF50",  # Verde
            "rejeitado": "#f44336"  # Vermelho
        }

        cor = cores.get(estado, "gray")

        self.estado_label.configure(text=estado_texto, fg_color=cor)

    def validar_campos(self):
        """Valida campos obrigatórios"""
        # Owner
        owner = self.owner_dropdown.get()
        if not owner or owner.strip() == "":
            messagebox.showerror("Erro", "Owner é obrigatório!")
            return False

        # Cliente
        cliente_texto = self.cliente_autocomplete.get_value()
        if not cliente_texto or cliente_texto.strip() == "":
            messagebox.showerror("Erro", "Cliente é obrigatório!")
            return False

        if cliente_texto not in self.clientes_map:
            messagebox.showerror("Erro", "Cliente inválido! Selecione da lista.")
            return False

        # Data Criação
        data_criacao = self.data_criacao_picker.get_date()
        if not data_criacao:
            messagebox.showerror("Erro", "Data de Criação é obrigatória!")
            return False

        return True

    def obter_dados_formulario(self):
        """Obtém dados do formulário"""
        cliente_texto = self.cliente_autocomplete.get_value()
        cliente_id = self.clientes_map.get(cliente_texto)

        data = {
            "cliente_id": cliente_id,
            "data_criacao": self.data_criacao_picker.get_date(),
            "data_evento": self.data_evento_entry.get().strip() or None,
            "local_evento": self.local_evento_entry.get().strip() or None,
            "status": "rascunho"
        }

        return data

    def gravar_rascunho(self):
        """Grava orçamento como rascunho"""
        if not self.validar_campos():
            return

        data = self.obter_dados_formulario()

        try:
            if self.orcamento_id:
                # Atualizar existente
                sucesso, orc, erro = self.manager.atualizar_orcamento(self.orcamento_id, **data)
            else:
                # Criar novo
                codigo = self.codigo_entry.get()
                data["codigo"] = codigo
                sucesso, orc, erro = self.manager.criar_orcamento(**data)

                if sucesso:
                    self.orcamento_id = orc.id
                    self.orcamento = orc

            if sucesso:
                messagebox.showinfo("Sucesso", "Orçamento guardado com sucesso!")
                self.alteracoes_pendentes = False

                # Recarregar dados
                if self.orcamento_id:
                    self.orcamento = self.manager.obter_orcamento(self.orcamento_id)
                    self.atualizar_estado_badge()
                    self.atualizar_botoes_acao()
                    self.carregar_items_empresa()
            else:
                messagebox.showerror("Erro", f"Erro ao gravar: {erro}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gravar orçamento: {str(e)}")

    def aprovar(self):
        """Aprovar orçamento"""
        # Validar totais
        if not self.orcamento_id:
            return

        items_empresa = self.db_session.query(OrcamentoItem).filter(
            OrcamentoItem.orcamento_id == self.orcamento_id
        ).all()
        total_empresa = sum(float(item.total) for item in items_empresa)
        total_cliente = 0.00  # TODO: Calcular quando tiver items cliente

        diferenca = abs(total_cliente - total_empresa)

        if diferenca > 0.01:
            if not messagebox.askyesno(
                "Aviso",
                f"Os totais CLIENTE (€{total_cliente:.2f}) e EMPRESA (€{total_empresa:.2f}) não coincidem.\n"
                f"Diferença: €{diferenca:.2f}\n\n"
                "Deseja aprovar mesmo assim?"
            ):
                return

        try:
            sucesso, orc, erro = self.manager.atualizar_orcamento(
                self.orcamento_id,
                status="aprovado"
            )

            if sucesso:
                messagebox.showinfo("Sucesso", "Orçamento aprovado!")
                self.orcamento = self.manager.obter_orcamento(self.orcamento_id)
                self.atualizar_estado_badge()
                self.atualizar_botoes_acao()
            else:
                messagebox.showerror("Erro", f"Erro ao aprovar: {erro}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aprovar orçamento: {str(e)}")

    def anular(self):
        """Anular orçamento"""
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja anular este orçamento?"):
            return

        try:
            sucesso, orc, erro = self.manager.atualizar_orcamento(
                self.orcamento_id,
                status="rejeitado"  # Usar "rejeitado" como anulado
            )

            if sucesso:
                messagebox.showinfo("Sucesso", "Orçamento anulado!")
                self.orcamento = self.manager.obter_orcamento(self.orcamento_id)
                self.atualizar_estado_badge()
                self.atualizar_botoes_acao()
            else:
                messagebox.showerror("Erro", f"Erro ao anular: {erro}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao anular orçamento: {str(e)}")

    def voltar(self):
        """Volta para lista"""
        if self.alteracoes_pendentes:
            if not messagebox.askyesno("Confirmar", "Existem alterações não guardadas. Deseja sair sem gravar?"):
                return

        self.master.show_screen("orcamentos")

    def atualizar_botoes_acao(self):
        """Atualiza botões baseado no estado"""
        # Hide todos primeiro
        self.aprovar_btn.pack_forget()
        self.anular_btn.pack_forget()

        if not self.orcamento:
            # Novo orçamento - apenas botão gravar
            return

        estado = self.orcamento.status

        if estado == "rascunho":
            # Mostrar aprovar
            self.aprovar_btn.pack(side="left", padx=(0, 10))
        elif estado == "aprovado" or estado == "enviado":
            # Mostrar anular
            self.anular_btn.pack(side="left", padx=(0, 10))
        elif estado == "rejeitado":
            # Anulado - nenhum botão
            pass

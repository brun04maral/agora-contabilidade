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
from ui.components.date_range_picker_dropdown import DateRangePickerDropdown
from typing import Optional
from datetime import date
from tkinter import messagebox
from decimal import Decimal


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

        # TODO: Adicionar campo owner (BA/RR) ao modelo Orcamento
        # Por agora, implementar dropdown mas não gravar
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
        self.data_evento_picker = DateRangePickerDropdown(
            fields_frame,
            placeholder="Selecionar período do evento..."
        )
        self.data_evento_picker.grid(row=2, column=3, padx=(0, 20), pady=(0, 10), sticky="ew")

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

        # Tab Cliente
        self.tab_cliente = self.tabview.add("👤 CLIENTE")

        # Header com botão Nova Secção
        header_cliente = ctk.CTkFrame(self.tab_cliente, fg_color="transparent")
        header_cliente.pack(fill="x", padx=20, pady=(10, 0))

        self.nova_secao_btn = ctk.CTkButton(
            header_cliente,
            text="➕ Nova Secção",
            command=self.adicionar_secao,
            width=140,
            height=32,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.nova_secao_btn.pack(side="left")

        # Área scrollável para secções e items
        self.secoes_scroll = ctk.CTkScrollableFrame(
            self.tab_cliente,
            fg_color="transparent"
        )
        self.secoes_scroll.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        # Total Cliente (sempre no fundo)
        total_cliente_frame = ctk.CTkFrame(self.tab_cliente)
        total_cliente_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        self.total_cliente_label = ctk.CTkLabel(
            total_cliente_frame,
            text="TOTAL CLIENTE: €0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        self.total_cliente_label.pack(pady=10)

        # Tab Empresa
        self.tab_empresa = self.tabview.add("🏢 EMPRESA")

        # Header com botões
        header_empresa = ctk.CTkFrame(self.tab_empresa, fg_color="transparent")
        header_empresa.pack(fill="x", padx=20, pady=(10, 0))

        self.nova_reparticao_btn = ctk.CTkButton(
            header_empresa,
            text="➕ Nova Repartição",
            command=self.adicionar_reparticao,
            width=160,
            height=32,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.nova_reparticao_btn.pack(side="left", padx=(0, 10))

        self.reparticao_auto_btn = ctk.CTkButton(
            header_empresa,
            text="⚡ Repartição Automática",
            command=self.reparticao_automatica,
            width=180,
            height=32,
            fg_color="#2196F3",
            hover_color="#0b7dda"
        )
        self.reparticao_auto_btn.pack(side="left")

        # Área scrollável para repartições
        self.reparticoes_scroll = ctk.CTkScrollableFrame(
            self.tab_empresa,
            fg_color="transparent"
        )
        self.reparticoes_scroll.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        # Total Empresa
        total_empresa_frame = ctk.CTkFrame(self.tab_empresa)
        total_empresa_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        self.total_empresa_label = ctk.CTkLabel(
            total_empresa_frame,
            text="TOTAL EMPRESA: €0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        self.total_empresa_label.pack(pady=(10, 5))

        # Label de aviso quando totais não coincidem
        self.validacao_label = ctk.CTkLabel(
            total_empresa_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#f44336"
        )
        self.validacao_label.pack(pady=(0, 10))

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

        # TODO: Carregar owner quando campo existir no modelo
        # self.owner_dropdown.set(self.orcamento.owner)

        # Cliente
        if self.orcamento.cliente:
            cliente_key = f"{self.orcamento.cliente.numero} - {self.orcamento.cliente.nome}"
            self.cliente_autocomplete.set(cliente_key)

        # Data Criação
        if self.orcamento.data_criacao:
            self.data_criacao_picker.set_date(self.orcamento.data_criacao)

        # Data Evento (o texto já está formatado no BD)
        if self.orcamento.data_evento:
            # Inserir texto formatado diretamente no entry do picker
            self.data_evento_picker.entry.delete(0, "end")
            self.data_evento_picker.entry.insert(0, self.orcamento.data_evento)

        # Local Evento
        if self.orcamento.local_evento:
            self.local_evento_entry.delete(0, "end")
            self.local_evento_entry.insert(0, self.orcamento.local_evento)

        # Atualizar estado badge
        self.atualizar_estado_badge()

        # Atualizar botões
        self.atualizar_botoes_acao()

        # Reset flag
        self.alteracoes_pendentes = False

        # Carregar secções e items
        self.carregar_secoes_items()

        # Carregar repartições
        self.carregar_reparticoes()

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
        cliente_texto = self.cliente_autocomplete.get()
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
        cliente_texto = self.cliente_autocomplete.get()
        cliente_id = self.clientes_map.get(cliente_texto)

        data = {
            "cliente_id": cliente_id,
            "data_criacao": self.data_criacao_picker.get_date(),
            "data_evento": self.data_evento_picker.get().strip() or None,
            "local_evento": self.local_evento_entry.get().strip() or None,
            "status": "rascunho"
        }

        # TODO: Adicionar owner quando campo existir no modelo
        # data["owner"] = self.owner_dropdown.get()

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
                    # Carregar secções (para novo orçamento)
                    self.carregar_secoes_items()
            else:
                messagebox.showerror("Erro", f"Erro ao gravar: {erro}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gravar orçamento: {str(e)}")

    def aprovar(self):
        """Aprovar orçamento (placeholder)"""
        messagebox.showinfo("Info", "Aprovação será implementada na próxima fase")

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

        # Hierarchy: self (OrcamentoFormScreen) -> master (content_frame) -> master (MainWindow)
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("orcamentos")
        else:
            messagebox.showerror("Erro", "Não foi possível voltar para a lista de orçamentos")

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

    # ==================== Gestão de Secções e Items ====================

    def carregar_secoes_items(self):
        """Carrega e renderiza todas as secções e items"""
        if not self.orcamento_id:
            # Não há orçamento ainda
            return

        # Limpar área de secções
        for widget in self.secoes_scroll.winfo_children():
            widget.destroy()

        # Obter secções principais (sem parent)
        secoes = self.manager.obter_secoes(self.orcamento_id)
        secoes_principais = [s for s in secoes if s.parent_id is None]

        if not secoes_principais:
            # Mostrar mensagem quando não há secções
            msg_label = ctk.CTkLabel(
                self.secoes_scroll,
                text="Nenhuma secção ainda. Clique em 'Nova Secção' para começar.",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            msg_label.pack(pady=50)
        else:
            # Renderizar cada secção principal
            for secao in secoes_principais:
                self.render_secao(secao, level=0)

        # Atualizar total cliente
        self.atualizar_total_cliente()

    def render_secao(self, secao, level=0):
        """Renderiza uma secção recursivamente com seus items e subsecções"""
        indent = level * 20

        # Frame da secção
        secao_frame = ctk.CTkFrame(self.secoes_scroll)
        secao_frame.pack(fill="x", pady=5, padx=(indent, 0))

        # Header da secção
        header = ctk.CTkFrame(secao_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)

        # Nome da secção
        icon = "📂" if level == 0 else "  📁"
        nome_label = ctk.CTkLabel(
            header,
            text=f"{icon} {secao.nome}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        nome_label.pack(side="left", fill="x", expand=True)

        # Subtotal da secção
        items = self.manager.obter_itens(self.orcamento_id, secao.id)
        subtotal = sum(float(item.total) for item in items)

        subtotal_label = ctk.CTkLabel(
            header,
            text=f"Subtotal: €{subtotal:.2f}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4CAF50"
        )
        subtotal_label.pack(side="right", padx=(10, 0))

        # Botões de ação da secção
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=(0, 10))

        # Botão adicionar item
        add_item_btn = ctk.CTkButton(
            btn_frame,
            text="+ Item",
            command=lambda: self.adicionar_item_em_secao(secao.id),
            width=70,
            height=24,
            font=ctk.CTkFont(size=11)
        )
        add_item_btn.pack(side="left", padx=2)

        # Botão editar secção
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️",
            command=lambda: self.editar_secao(secao),
            width=30,
            height=24,
            font=ctk.CTkFont(size=11)
        )
        edit_btn.pack(side="left", padx=2)

        # Botão eliminar secção
        del_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            command=lambda: self.eliminar_secao(secao),
            width=30,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#f44336",
            hover_color="#da190b"
        )
        del_btn.pack(side="left", padx=2)

        # Renderizar items da secção
        if items:
            items_container = ctk.CTkFrame(secao_frame, fg_color="transparent")
            items_container.pack(fill="x", padx=(20, 10), pady=(0, 5))

            for item in items:
                self.render_item(items_container, item)

        # Renderizar subsecções (recursivo)
        secoes = self.manager.obter_secoes(self.orcamento_id)
        subsecoes = [s for s in secoes if s.parent_id == secao.id]

        if subsecoes:
            for subsecao in subsecoes:
                self.render_secao(subsecao, level=level+1)

    def render_item(self, container, item):
        """Renderiza um item"""
        item_frame = ctk.CTkFrame(container)
        item_frame.pack(fill="x", pady=2)

        # Info do item
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)

        # Descrição
        desc_label = ctk.CTkLabel(
            info_frame,
            text=f"• {item.descricao}",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        desc_label.pack(side="left", fill="x", expand=True)

        # Cálculo detalhado
        desconto_str = f" × (1 - {float(item.desconto*100):.0f}%)" if item.desconto > 0 else ""
        calculo = f"{item.quantidade} × {item.dias} dias × €{float(item.preco_unitario):.2f}{desconto_str} = €{float(item.total):.2f}"

        calc_label = ctk.CTkLabel(
            info_frame,
            text=calculo,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        calc_label.pack(side="right", padx=(10, 0))

        # Botões de ação
        btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=(0, 10))

        # Botão editar
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️",
            command=lambda: self.editar_item(item),
            width=30,
            height=22,
            font=ctk.CTkFont(size=10)
        )
        edit_btn.pack(side="left", padx=2)

        # Botão eliminar
        del_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            command=lambda: self.eliminar_item(item),
            width=30,
            height=22,
            font=ctk.CTkFont(size=10),
            fg_color="#f44336",
            hover_color="#da190b"
        )
        del_btn.pack(side="left", padx=2)

    def atualizar_total_cliente(self):
        """Atualiza o total do cliente (soma de todos os items)"""
        if not self.orcamento_id:
            self.total_cliente_label.configure(text="TOTAL CLIENTE: €0.00")
            return

        # Obter todos os items
        items = self.manager.obter_itens(self.orcamento_id)
        total = sum(float(item.total) for item in items)

        self.total_cliente_label.configure(text=f"TOTAL CLIENTE: €{total:.2f}")

        # Validar totais (se repartições existirem)
        self.validar_totais()

    # ==================== CRUD de Secções ====================

    def adicionar_secao(self):
        """Abre dialog para adicionar nova secção"""
        if not self.orcamento_id:
            messagebox.showwarning("Aviso", "Grave o orçamento primeiro antes de adicionar secções.")
            return

        dialog = SecaoDialog(self, self.manager, self.orcamento_id)
        self.wait_window(dialog)

        if dialog.secao_criada:
            self.alteracoes_pendentes = True
            self.carregar_secoes_items()

    def editar_secao(self, secao):
        """Abre dialog para editar secção"""
        dialog = SecaoDialog(self, self.manager, self.orcamento_id, secao=secao)
        self.wait_window(dialog)

        if dialog.secao_atualizada:
            self.alteracoes_pendentes = True
            self.carregar_secoes_items()

    def eliminar_secao(self, secao):
        """Elimina secção (e seus items em cascade)"""
        if not messagebox.askyesno("Confirmar", f"Eliminar secção '{secao.nome}' e todos os seus items?"):
            return

        sucesso, erro = self.manager.eliminar_secao(secao.id)

        if sucesso:
            messagebox.showinfo("Sucesso", "Secção eliminada!")
            self.alteracoes_pendentes = True
            self.carregar_secoes_items()
        else:
            messagebox.showerror("Erro", f"Erro ao eliminar: {erro}")

    # ==================== CRUD de Items ====================

    def adicionar_item_em_secao(self, secao_id):
        """Abre dialog para adicionar item na secção"""
        dialog = ItemDialog(self, self.manager, self.orcamento_id, secao_id)
        self.wait_window(dialog)

        if dialog.item_criado:
            self.alteracoes_pendentes = True
            self.carregar_secoes_items()

    def editar_item(self, item):
        """Abre dialog para editar item"""
        dialog = ItemDialog(self, self.manager, self.orcamento_id, item.secao_id, item=item)
        self.wait_window(dialog)

        if dialog.item_atualizado:
            self.alteracoes_pendentes = True
            self.carregar_secoes_items()

    def eliminar_item(self, item):
        """Elimina item"""
        if not messagebox.askyesno("Confirmar", f"Eliminar item '{item.descricao}'?"):
            return

        sucesso, erro = self.manager.eliminar_item(item.id)

        if sucesso:
            messagebox.showinfo("Sucesso", "Item eliminado!")
            self.alteracoes_pendentes = True
            self.carregar_secoes_items()
        else:
            messagebox.showerror("Erro", f"Erro ao eliminar: {erro}")

    # ==================== Métodos para Repartições (Tab EMPRESA) ====================

    def carregar_reparticoes(self):
        """Carrega e renderiza todas as repartições"""
        if not self.orcamento_id:
            return

        # Limpar área
        for widget in self.reparticoes_scroll.winfo_children():
            widget.destroy()

        # Obter repartições
        reparticoes = self.manager.obter_reparticoes(self.orcamento_id)

        if not reparticoes:
            msg_label = ctk.CTkLabel(
                self.reparticoes_scroll,
                text="Nenhuma repartição ainda. Clique em 'Nova Repartição' ou 'Repartição Automática'.",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            msg_label.pack(pady=50)
        else:
            for reparticao in reparticoes:
                self.render_reparticao(reparticao)

        # Atualizar total e validação
        self.atualizar_total_empresa()
        self.validar_totais()

    def render_reparticao(self, reparticao):
        """Renderiza uma repartição na lista"""
        # Frame da repartição
        reparticao_frame = ctk.CTkFrame(
            self.reparticoes_scroll,
            fg_color=("#f0f0f0", "#2b2b2b"),
            corner_radius=6
        )
        reparticao_frame.pack(fill="x", pady=5, padx=5)

        # Grid layout
        reparticao_frame.grid_columnconfigure(1, weight=1)

        # Ícone e entidade
        icon_map = {
            "BA": "🏢",
            "RR": "🏛️",
            "Agora": "⚡",
            "Freelancers": "👥",
            "Despesas": "💰"
        }
        icon = icon_map.get(reparticao.entidade, "💼")

        entidade_label = ctk.CTkLabel(
            reparticao_frame,
            text=f"{icon} {reparticao.entidade}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        entidade_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        # Valor
        valor_label = ctk.CTkLabel(
            reparticao_frame,
            text=f"€{float(reparticao.valor):.2f}",
            font=ctk.CTkFont(size=13),
            anchor="w",
            text_color=("#2c3e50", "#ecf0f1")
        )
        valor_label.grid(row=1, column=0, padx=15, pady=(0, 5), sticky="w")

        # Percentagem (se existir)
        if reparticao.percentagem:
            percent_label = ctk.CTkLabel(
                reparticao_frame,
                text=f"({float(reparticao.percentagem):.1f}%)",
                font=ctk.CTkFont(size=12),
                text_color="gray",
                anchor="w"
            )
            percent_label.grid(row=1, column=1, padx=(5, 15), pady=(0, 5), sticky="w")

        # Botões de ação
        btn_frame = ctk.CTkFrame(reparticao_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=5)

        editar_btn = ctk.CTkButton(
            btn_frame,
            text="✏️",
            command=lambda r=reparticao: self.editar_reparticao(r),
            width=40,
            height=28,
            fg_color="transparent",
            hover_color=("#e0e0e0", "#3a3a3a")
        )
        editar_btn.pack(side="left", padx=2)

        eliminar_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            command=lambda r=reparticao: self.eliminar_reparticao(r),
            width=40,
            height=28,
            fg_color="transparent",
            hover_color=("#ffcdd2", "#d32f2f"),
            text_color=("#d32f2f", "#ff5252")
        )
        eliminar_btn.pack(side="left", padx=2)

    def adicionar_reparticao(self):
        """Abre dialog para adicionar nova repartição"""
        if not self.orcamento_id:
            messagebox.showwarning("Aviso", "Grave o orçamento primeiro!")
            return

        # Obter entidades já usadas
        reparticoes_existentes = self.manager.obter_reparticoes(self.orcamento_id)
        entidades_usadas = {r.entidade for r in reparticoes_existentes}

        dialog = ReparticaoDialog(
            self,
            self.manager,
            self.orcamento_id,
            entidades_usadas=entidades_usadas
        )
        self.wait_window(dialog)

        if dialog.sucesso:
            self.alteracoes_pendentes = True
            self.carregar_reparticoes()

    def editar_reparticao(self, reparticao):
        """Abre dialog para editar repartição"""
        # Obter entidades já usadas (exceto a atual)
        reparticoes_existentes = self.manager.obter_reparticoes(self.orcamento_id)
        entidades_usadas = {r.entidade for r in reparticoes_existentes if r.id != reparticao.id}

        dialog = ReparticaoDialog(
            self,
            self.manager,
            self.orcamento_id,
            reparticao=reparticao,
            entidades_usadas=entidades_usadas
        )
        self.wait_window(dialog)

        if dialog.sucesso:
            self.alteracoes_pendentes = True
            self.carregar_reparticoes()

    def eliminar_reparticao(self, reparticao):
        """Elimina repartição após confirmação"""
        if not messagebox.askyesno("Confirmar", f"Eliminar repartição '{reparticao.entidade}'?"):
            return

        sucesso, erro = self.manager.eliminar_reparticao(reparticao.id)

        if sucesso:
            messagebox.showinfo("Sucesso", "Repartição eliminada!")
            self.alteracoes_pendentes = True
            self.carregar_reparticoes()
        else:
            messagebox.showerror("Erro", f"Erro ao eliminar: {erro}")

    def reparticao_automatica(self):
        """Cria repartições automáticas com percentagens padrão"""
        if not self.orcamento_id:
            messagebox.showwarning("Aviso", "Grave o orçamento primeiro!")
            return

        # Confirmar ação
        reparticoes_existentes = self.manager.obter_reparticoes(self.orcamento_id)
        if reparticoes_existentes:
            if not messagebox.askyesno(
                "Confirmar",
                "Já existem repartições. Deseja substituí-las pela repartição automática?"
            ):
                return

            # Eliminar repartições existentes
            for rep in reparticoes_existentes:
                self.manager.eliminar_reparticao(rep.id)

        # Obter total cliente
        items = self.manager.obter_itens(self.orcamento_id)
        total_cliente = sum(float(item.total) for item in items)

        if total_cliente == 0:
            messagebox.showwarning("Aviso", "Total do cliente é €0. Adicione items primeiro!")
            return

        # Percentagens padrão
        percentagens_padrao = {
            "BA": Decimal("40.0"),
            "RR": Decimal("30.0"),
            "Agora": Decimal("15.0"),
            "Freelancers": Decimal("10.0"),
            "Despesas": Decimal("5.0")
        }

        # Criar repartições
        ordem = 0
        for entidade, percentagem in percentagens_padrao.items():
            valor = Decimal(str(total_cliente)) * (percentagem / Decimal("100"))
            self.manager.adicionar_reparticao(
                orcamento_id=self.orcamento_id,
                entidade=entidade,
                valor=valor,
                percentagem=percentagem,
                ordem=ordem
            )
            ordem += 1

        messagebox.showinfo("Sucesso", "Repartição automática criada!")
        self.alteracoes_pendentes = True
        self.carregar_reparticoes()

    def atualizar_total_empresa(self):
        """Atualiza o total da empresa (soma de todas as repartições)"""
        if not self.orcamento_id:
            self.total_empresa_label.configure(text="TOTAL EMPRESA: €0.00")
            return

        reparticoes = self.manager.obter_reparticoes(self.orcamento_id)
        total = sum(float(r.valor) for r in reparticoes)
        self.total_empresa_label.configure(text=f"TOTAL EMPRESA: €{total:.2f}")

    def validar_totais(self):
        """Valida se TOTAL EMPRESA == TOTAL CLIENTE"""
        if not self.orcamento_id:
            self.validacao_label.configure(text="")
            return

        # Obter totais
        items = self.manager.obter_itens(self.orcamento_id)
        total_cliente = sum(float(item.total) for item in items)

        reparticoes = self.manager.obter_reparticoes(self.orcamento_id)
        total_empresa = sum(float(r.valor) for r in reparticoes)

        # Comparar com tolerância de 0.01 (por causa de arredondamentos)
        diferenca = abs(total_cliente - total_empresa)

        if diferenca < 0.01:
            # Totais coincidem
            self.validacao_label.configure(text="✓ Totais coincidem", text_color="#4CAF50")
            self.total_empresa_label.configure(text_color="#4CAF50")
        else:
            # Totais não coincidem
            self.validacao_label.configure(
                text=f"⚠️ ATENÇÃO: Diferença de €{diferenca:.2f}",
                text_color="#f44336"
            )
            self.total_empresa_label.configure(text_color="#f44336")


# ==================== Diálogos ====================

class SecaoDialog(ctk.CTkToplevel):
    """Dialog para criar/editar secção"""

    def __init__(self, parent, manager, orcamento_id, secao=None):
        super().__init__(parent)

        self.manager = manager
        self.orcamento_id = orcamento_id
        self.secao = secao
        self.secao_criada = False
        self.secao_atualizada = False

        # Window config
        self.title("Editar Secção" if secao else "Nova Secção")
        self.geometry("500x400")
        self.resizable(False, False)

        # Center window
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"500x400+{x}+{y}")

        # Create widgets
        self.create_widgets()

        # Load data if editing
        if self.secao:
            self.load_data()

    def create_widgets(self):
        """Create dialog widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="✏️ Editar Secção" if self.secao else "➕ Nova Secção",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(0, 20))

        # Form
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)

        # Nome
        ctk.CTkLabel(form_frame, text="Nome: *").pack(anchor="w", pady=(0, 5))
        self.nome_entry = ctk.CTkEntry(form_frame, placeholder_text="Nome da secção...")
        self.nome_entry.pack(fill="x", pady=(0, 15))

        # Tipo
        ctk.CTkLabel(form_frame, text="Tipo: *").pack(anchor="w", pady=(0, 5))
        self.tipo_combo = ctk.CTkComboBox(
            form_frame,
            values=["servicos", "equipamento", "despesas", "video", "som", "iluminacao"],
            state="readonly"
        )
        self.tipo_combo.set("servicos")
        self.tipo_combo.pack(fill="x", pady=(0, 15))

        # Parent (opcional)
        ctk.CTkLabel(form_frame, text="Secção Pai (opcional):").pack(anchor="w", pady=(0, 5))

        # Obter secções existentes
        secoes = self.manager.obter_secoes(self.orcamento_id)
        secoes_nomes = ["(Nenhuma)"] + [s.nome for s in secoes if s.id != (self.secao.id if self.secao else None)]
        self.secoes_map = {"(Nenhuma)": None}
        self.secoes_map.update({s.nome: s.id for s in secoes if s.id != (self.secao.id if self.secao else None)})

        self.parent_combo = ctk.CTkComboBox(
            form_frame,
            values=secoes_nomes,
            state="readonly"
        )
        self.parent_combo.set("(Nenhuma)")
        self.parent_combo.pack(fill="x", pady=(0, 15))

        # Ordem
        ctk.CTkLabel(form_frame, text="Ordem:").pack(anchor="w", pady=(0, 5))
        self.ordem_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        self.ordem_entry.insert(0, "0")
        self.ordem_entry.pack(fill="x", pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            width=120
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Gravar",
            command=self.gravar,
            width=120,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        save_btn.pack(side="left")

    def load_data(self):
        """Load secao data for editing"""
        self.nome_entry.insert(0, self.secao.nome)
        self.tipo_combo.set(self.secao.tipo)
        self.ordem_entry.delete(0, "end")
        self.ordem_entry.insert(0, str(self.secao.ordem))

        if self.secao.parent_id:
            # Find parent name
            secoes = self.manager.obter_secoes(self.orcamento_id)
            parent = next((s for s in secoes if s.id == self.secao.parent_id), None)
            if parent:
                self.parent_combo.set(parent.nome)

    def validar(self):
        """Validate form"""
        if not self.nome_entry.get().strip():
            messagebox.showerror("Erro", "Nome é obrigatório!")
            return False

        return True

    def gravar(self):
        """Save secao"""
        if not self.validar():
            return

        data = {
            "nome": self.nome_entry.get().strip(),
            "tipo": self.tipo_combo.get(),
            "ordem": int(self.ordem_entry.get() or 0),
            "parent_id": self.secoes_map.get(self.parent_combo.get())
        }

        try:
            if self.secao:
                # Atualizar
                sucesso, _, erro = self.manager.atualizar_secao(self.secao.id, **data)
                self.secao_atualizada = sucesso
            else:
                # Criar
                sucesso, _, erro = self.manager.adicionar_secao(
                    self.orcamento_id,
                    **data
                )
                self.secao_criada = sucesso

            if sucesso:
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro: {erro}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")


class ItemDialog(ctk.CTkToplevel):
    """Dialog para criar/editar item"""

    def __init__(self, parent, manager, orcamento_id, secao_id, item=None):
        super().__init__(parent)

        self.manager = manager
        self.orcamento_id = orcamento_id
        self.secao_id = secao_id
        self.item = item
        self.item_criado = False
        self.item_atualizado = False

        # Window config
        self.title("Editar Item" if item else "Novo Item")
        self.geometry("600x500")
        self.resizable(False, False)

        # Center window
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"600x500+{x}+{y}")

        # Create widgets
        self.create_widgets()

        # Load data if editing
        if self.item:
            self.load_data()

    def create_widgets(self):
        """Create dialog widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="✏️ Editar Item" if self.item else "➕ Novo Item",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(0, 20))

        # Form
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)

        # Descrição
        ctk.CTkLabel(form_frame, text="Descrição: *").pack(anchor="w", pady=(0, 5))
        self.descricao_entry = ctk.CTkEntry(form_frame, placeholder_text="Descrição do item...")
        self.descricao_entry.pack(fill="x", pady=(0, 15))

        # Grid para campos numéricos
        grid_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 15))
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=1)

        # Quantidade
        ctk.CTkLabel(grid_frame, text="Quantidade: *").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.quantidade_entry = ctk.CTkEntry(grid_frame, placeholder_text="1")
        self.quantidade_entry.insert(0, "1")
        self.quantidade_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))

        # Dias
        ctk.CTkLabel(grid_frame, text="Dias: *").grid(row=0, column=1, sticky="w", padx=(0, 10))
        self.dias_entry = ctk.CTkEntry(grid_frame, placeholder_text="1")
        self.dias_entry.insert(0, "1")
        self.dias_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 15))

        # Preço Unitário
        ctk.CTkLabel(grid_frame, text="Preço Unitário (€): *").grid(row=0, column=2, sticky="w")
        self.preco_entry = ctk.CTkEntry(grid_frame, placeholder_text="0.00")
        self.preco_entry.grid(row=1, column=2, sticky="ew", pady=(0, 15))

        # Desconto (%)
        ctk.CTkLabel(form_frame, text="Desconto (%):").pack(anchor="w", pady=(0, 5))
        self.desconto_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        self.desconto_entry.insert(0, "0")
        self.desconto_entry.pack(fill="x", pady=(0, 15))

        # Ordem
        ctk.CTkLabel(form_frame, text="Ordem:").pack(anchor="w", pady=(0, 5))
        self.ordem_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        self.ordem_entry.insert(0, "0")
        self.ordem_entry.pack(fill="x", pady=(0, 20))

        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            width=120
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Gravar",
            command=self.gravar,
            width=120,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        save_btn.pack(side="left")

    def load_data(self):
        """Load item data for editing"""
        self.descricao_entry.insert(0, self.item.descricao)
        self.quantidade_entry.delete(0, "end")
        self.quantidade_entry.insert(0, str(self.item.quantidade))
        self.dias_entry.delete(0, "end")
        self.dias_entry.insert(0, str(self.item.dias))
        self.preco_entry.delete(0, "end")
        self.preco_entry.insert(0, str(float(self.item.preco_unitario)))
        self.desconto_entry.delete(0, "end")
        self.desconto_entry.insert(0, str(float(self.item.desconto * 100)))
        self.ordem_entry.delete(0, "end")
        self.ordem_entry.insert(0, str(self.item.ordem))

    def validar(self):
        """Validate form"""
        if not self.descricao_entry.get().strip():
            messagebox.showerror("Erro", "Descrição é obrigatória!")
            return False

        try:
            int(self.quantidade_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro!")
            return False

        try:
            int(self.dias_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Dias deve ser um número inteiro!")
            return False

        try:
            float(self.preco_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser um número!")
            return False

        try:
            desconto = float(self.desconto_entry.get())
            if desconto < 0 or desconto > 100:
                messagebox.showerror("Erro", "Desconto deve estar entre 0 e 100!")
                return False
        except ValueError:
            messagebox.showerror("Erro", "Desconto deve ser um número!")
            return False

        return True

    def gravar(self):
        """Save item"""
        if not self.validar():
            return

        data = {
            "descricao": self.descricao_entry.get().strip(),
            "quantidade": int(self.quantidade_entry.get()),
            "dias": int(self.dias_entry.get()),
            "preco_unitario": Decimal(self.preco_entry.get()),
            "desconto": Decimal(self.desconto_entry.get()) / 100,  # Converter % para decimal
            "ordem": int(self.ordem_entry.get() or 0)
        }

        try:
            if self.item:
                # Atualizar
                sucesso, _, erro = self.manager.atualizar_item(self.item.id, **data)
                self.item_atualizado = sucesso
            else:
                # Criar
                sucesso, _, erro = self.manager.adicionar_item(
                    self.orcamento_id,
                    self.secao_id,
                    **data
                )
                self.item_criado = sucesso

            if sucesso:
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro: {erro}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")


class ReparticaoDialog(ctk.CTkToplevel):
    """Dialog para criar/editar repartição"""

    def __init__(self, parent, manager, orcamento_id, reparticao=None, entidades_usadas=None):
        super().__init__(parent)

        self.manager = manager
        self.orcamento_id = orcamento_id
        self.reparticao = reparticao
        self.entidades_usadas = entidades_usadas or set()
        self.sucesso = False

        # Configurar janela
        self.title("Editar Repartição" if reparticao else "Nova Repartição")
        self.geometry("450x300")
        self.resizable(False, False)

        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        # Tornar modal
        self.transient(parent)
        self.grab_set()

        # UI
        self.criar_ui()

        # Preencher se edição
        if reparticao:
            self.carregar_dados()

    def criar_ui(self):
        """Cria interface do dialog"""
        # Container principal
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        # Entidade (dropdown com opções fixas)
        ctk.CTkLabel(
            container,
            text="Entidade:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Opções de entidades
        entidades_disponiveis = ["BA", "RR", "Agora", "Freelancers", "Despesas"]

        # Se editando, incluir a entidade atual mesmo se já usada
        if self.reparticao:
            entidades_disponiveis_filtradas = [self.reparticao.entidade] + [
                e for e in entidades_disponiveis if e not in self.entidades_usadas
            ]
        else:
            # Se criando, filtrar entidades já usadas
            entidades_disponiveis_filtradas = [
                e for e in entidades_disponiveis if e not in self.entidades_usadas
            ]

        if not entidades_disponiveis_filtradas:
            # Nenhuma entidade disponível
            ctk.CTkLabel(
                container,
                text="Todas as entidades já foram utilizadas!",
                text_color="red"
            ).grid(row=1, column=0, sticky="w", pady=(0, 15))

            # Botão fechar
            ctk.CTkButton(
                container,
                text="Fechar",
                command=self.destroy,
                width=120,
                height=35
            ).grid(row=2, column=0, pady=(20, 0))
            return

        self.entidade_var = ctk.StringVar(value=entidades_disponiveis_filtradas[0])
        self.entidade_dropdown = ctk.CTkOptionMenu(
            container,
            variable=self.entidade_var,
            values=entidades_disponiveis_filtradas,
            width=200,
            height=35
        )
        self.entidade_dropdown.grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Se editando, desabilitar mudança de entidade
        if self.reparticao:
            self.entidade_dropdown.configure(state="disabled")

        # Valor
        ctk.CTkLabel(
            container,
            text="Valor (€):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.valor_entry = ctk.CTkEntry(
            container,
            placeholder_text="0.00",
            width=200,
            height=35
        )
        self.valor_entry.grid(row=3, column=0, sticky="w", pady=(0, 15))

        # Percentagem (opcional)
        ctk.CTkLabel(
            container,
            text="Percentagem (%) [opcional]:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=4, column=0, sticky="w", pady=(0, 5))

        self.percentagem_entry = ctk.CTkEntry(
            container,
            placeholder_text="0.0",
            width=200,
            height=35
        )
        self.percentagem_entry.grid(row=5, column=0, sticky="w", pady=(0, 20))

        # Botões
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.grid(row=6, column=0, sticky="w")

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            width=100,
            height=35,
            fg_color="gray",
            hover_color="#5a5a5a"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Gravar",
            command=self.gravar,
            width=100,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="left")

    def carregar_dados(self):
        """Carrega dados da repartição para edição"""
        if not self.reparticao:
            return

        self.entidade_var.set(self.reparticao.entidade)
        self.valor_entry.insert(0, str(float(self.reparticao.valor)))

        if self.reparticao.percentagem:
            self.percentagem_entry.insert(0, str(float(self.reparticao.percentagem)))

    def gravar(self):
        """Valida e grava repartição"""
        try:
            # Validar campos
            entidade = self.entidade_var.get().strip()
            if not entidade:
                messagebox.showwarning("Aviso", "Selecione uma entidade!")
                return

            valor_str = self.valor_entry.get().strip()
            if not valor_str:
                messagebox.showwarning("Aviso", "Preencha o valor!")
                return

            try:
                valor = Decimal(valor_str)
                if valor <= 0:
                    messagebox.showwarning("Aviso", "Valor deve ser maior que zero!")
                    return
            except:
                messagebox.showwarning("Aviso", "Valor inválido!")
                return

            # Percentagem (opcional)
            percentagem = None
            percentagem_str = self.percentagem_entry.get().strip()
            if percentagem_str:
                try:
                    percentagem = Decimal(percentagem_str)
                    if percentagem < 0 or percentagem > 100:
                        messagebox.showwarning("Aviso", "Percentagem deve estar entre 0 e 100!")
                        return
                except:
                    messagebox.showwarning("Aviso", "Percentagem inválida!")
                    return

            # Preparar dados
            data = {
                "entidade": entidade,
                "valor": valor,
                "percentagem": percentagem,
                "ordem": 0  # Ordem será ajustada automaticamente
            }

            # Gravar
            if self.reparticao:
                # Editar
                sucesso, _, erro = self.manager.atualizar_reparticao(
                    self.reparticao.id,
                    **data
                )
            else:
                # Criar
                sucesso, _, erro = self.manager.adicionar_reparticao(
                    self.orcamento_id,
                    **data
                )

            if sucesso:
                self.sucesso = True
                self.destroy()
            else:
                messagebox.showerror("Erro", f"Erro: {erro}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {str(e)}")

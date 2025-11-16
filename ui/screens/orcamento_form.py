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
from typing import Optional
from datetime import date
from tkinter import messagebox


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

        # Tab Cliente
        self.tab_cliente = self.tabview.add("👤 CLIENTE")
        placeholder_cliente = ctk.CTkLabel(
            self.tab_cliente,
            text="📑 Secções e Items serão implementados na próxima fase",
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

        # Tab Empresa
        self.tab_empresa = self.tabview.add("🏢 EMPRESA")
        placeholder_empresa = ctk.CTkLabel(
            self.tab_empresa,
            text="💼 Repartições serão implementadas na próxima fase",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        placeholder_empresa.pack(expand=True)

        # Total Empresa
        total_empresa_frame = ctk.CTkFrame(self.tab_empresa)
        total_empresa_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        self.total_empresa_label = ctk.CTkLabel(
            total_empresa_frame,
            text="TOTAL EMPRESA: €0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        self.total_empresa_label.pack(pady=10)

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

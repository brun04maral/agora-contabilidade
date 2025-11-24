# -*- coding: utf-8 -*-
"""
Tela de Formulário de Projeto - Screen dedicado para criar/editar projetos
Segue mesmo padrão de ui/screens/orcamento_form.py
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.projetos import ProjetosManager
from logic.clientes import ClientesManager
from ui.components.date_picker_dropdown import DatePickerDropdown
from ui.components.date_range_picker_dropdown import DateRangePickerDropdown
from database.models import TipoProjeto, EstadoProjeto
from typing import Optional
from datetime import date
from tkinter import messagebox
from decimal import Decimal


class ProjetoFormScreen(ctk.CTkFrame):
    """
    Screen para criar/editar projetos

    Navegação via MainWindow.show_screen("projeto_form", projeto_id=None/ID)
    """

    def __init__(self, parent, db_session: Session, projeto_id: Optional[int] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.projeto_id = projeto_id
        self.manager = ProjetosManager(db_session)
        self.clientes_manager = ClientesManager(db_session)

        # Estado
        self.projeto = None
        self.clientes_map = {}

        # Configure
        self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.create_widgets()

        # Load data se edição
        if projeto_id:
            self.carregar_projeto()

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
        # 2. CAMPOS DO PROJETO
        # ========================================
        self.create_fields(main_container)

        # ========================================
        # 3. FOOTER COM BOTÕES
        # ========================================
        self.create_footer(main_container)

    def create_header(self, parent):
        """Cria header com botão voltar e título"""
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
        titulo = "Novo Projeto" if not self.projeto_id else "Editar Projeto"
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=titulo,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=1, sticky="w")

    def create_fields(self, parent):
        """Cria campos do formulário"""
        fields_frame = ctk.CTkFrame(parent, fg_color="transparent")
        fields_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 20))
        fields_frame.grid_columnconfigure(0, weight=1)

        # Tipo e Responsável (mesma linha)
        tipo_owner_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        tipo_owner_frame.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        tipo_owner_frame.grid_columnconfigure((0, 1), weight=1)

        # Tipo
        ctk.CTkLabel(tipo_owner_frame, text="Tipo *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 12))
        self.tipo_dropdown = ctk.CTkOptionMenu(tipo_owner_frame, values=["Empresa", "Pessoal"], width=200, height=35)
        self.tipo_dropdown.grid(row=1, column=0, sticky="w", padx=(0, 12), pady=(8, 0))

        # Responsável
        ctk.CTkLabel(tipo_owner_frame, text="Responsável *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=1, sticky="w")
        self.owner_dropdown = ctk.CTkOptionMenu(tipo_owner_frame, values=["BA", "RR"], width=100, height=35)
        self.owner_dropdown.grid(row=1, column=1, sticky="w", pady=(8, 0))

        # Cliente
        ctk.CTkLabel(fields_frame, text="Cliente", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 8))

        clientes = self.manager.obter_clientes()
        cliente_options = ["(Nenhum)"] + [f"{c.numero} - {c.nome}" for c in clientes]
        self.cliente_dropdown = ctk.CTkOptionMenu(fields_frame, values=cliente_options, width=400, height=35)
        self.cliente_dropdown.grid(row=3, column=0, sticky="w", pady=(0, 18))
        self.clientes_map = {f"{c.numero} - {c.nome}": c.id for c in clientes}

        # Descrição
        ctk.CTkLabel(fields_frame, text="Descrição *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=4, column=0, sticky="w", pady=(0, 8))
        self.descricao_entry = ctk.CTkTextbox(fields_frame, height=90)
        self.descricao_entry.grid(row=5, column=0, sticky="ew", pady=(0, 18))

        # Valor
        ctk.CTkLabel(fields_frame, text="Valor sem IVA *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=6, column=0, sticky="w", pady=(0, 8))
        self.valor_entry = ctk.CTkEntry(fields_frame, placeholder_text="0.00", height=35)
        self.valor_entry.grid(row=7, column=0, sticky="ew", pady=(0, 18))

        # Datas
        datas_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        datas_frame.grid(row=8, column=0, sticky="ew", pady=(0, 18))
        datas_frame.grid_columnconfigure((0, 1), weight=1)

        # Período do projeto
        ctk.CTkLabel(datas_frame, text="Período do Projeto", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w")
        self.periodo_picker = DateRangePickerDropdown(datas_frame, placeholder="Selecionar período...")
        self.periodo_picker.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 12))

        # Data faturação
        ctk.CTkLabel(datas_frame, text="Data Faturação", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=2, column=0, sticky="w", padx=(0, 12))
        self.data_faturacao_picker = DatePickerDropdown(datas_frame, placeholder="Selecionar...")
        self.data_faturacao_picker.grid(row=3, column=0, sticky="ew", padx=(0, 12), pady=(8, 12))

        # Data vencimento
        ctk.CTkLabel(datas_frame, text="Data Vencimento", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=2, column=1, sticky="w")
        self.data_vencimento_picker = DatePickerDropdown(datas_frame, placeholder="Selecionar...")
        self.data_vencimento_picker.grid(row=3, column=1, sticky="ew", pady=(8, 12))

        # Estado
        ctk.CTkLabel(fields_frame, text="Estado *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=9, column=0, sticky="w", pady=(0, 8))
        self.estado_dropdown = ctk.CTkOptionMenu(fields_frame, values=["Ativo", "Finalizado", "Pago", "Anulado"], height=35)
        self.estado_dropdown.grid(row=10, column=0, sticky="w", pady=(0, 18))

        # Prémios
        premios_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        premios_frame.grid(row=11, column=0, sticky="ew", pady=(0, 18))
        premios_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(premios_frame, text="Prémio BA (€)", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 12))
        self.premio_bruno_entry = ctk.CTkEntry(premios_frame, placeholder_text="0.00", height=35)
        self.premio_bruno_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(8, 0))

        ctk.CTkLabel(premios_frame, text="Prémio RR (€)", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=1, sticky="w")
        self.premio_rafael_entry = ctk.CTkEntry(premios_frame, placeholder_text="0.00", height=35)
        self.premio_rafael_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))

        # Nota
        ctk.CTkLabel(fields_frame, text="Nota", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=12, column=0, sticky="w", pady=(0, 8))
        self.nota_entry = ctk.CTkTextbox(fields_frame, height=70)
        self.nota_entry.grid(row=13, column=0, sticky="ew", pady=(0, 10))

    def create_footer(self, parent):
        """Cria footer com botões"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(10, 30))

        # Botão Guardar
        save_btn = ctk.CTkButton(
            footer_frame,
            text="💾 Guardar",
            command=self.guardar,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#66BB6A", "#2E7D32")
        )
        save_btn.pack(side="left", padx=(0, 10))

        # Botão Cancelar
        cancel_btn = ctk.CTkButton(
            footer_frame,
            text="Cancelar",
            command=self.voltar,
            width=130,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=("#757575", "#616161"),
            hover_color=("#616161", "#424242")
        )
        cancel_btn.pack(side="left")

    def carregar_projeto(self):
        """Carrega dados do projeto para edição"""
        self.projeto = self.manager.obter_por_id(self.projeto_id)
        if not self.projeto:
            messagebox.showerror("Erro", "Projeto não encontrado!")
            self.voltar()
            return

        # Atualizar título
        self.title_label.configure(text=f"Editar Projeto {self.projeto.numero}")

        # Tipo e Owner
        tipo_label = "Empresa" if self.projeto.tipo == TipoProjeto.EMPRESA else "Pessoal"
        self.tipo_dropdown.set(tipo_label)
        self.owner_dropdown.set(self.projeto.owner)

        # Cliente
        if self.projeto.cliente:
            cliente_str = f"{self.projeto.cliente.numero} - {self.projeto.cliente.nome}"
            self.cliente_dropdown.set(cliente_str)

        # Descrição
        self.descricao_entry.insert("1.0", self.projeto.descricao or "")

        # Valor
        self.valor_entry.insert(0, str(self.projeto.valor_sem_iva))

        # Datas
        if self.projeto.data_inicio:
            self.periodo_picker.set_range(self.projeto.data_inicio, self.projeto.data_fim)
        if self.projeto.data_faturacao:
            self.data_faturacao_picker.set_date(self.projeto.data_faturacao)
        if self.projeto.data_vencimento:
            self.data_vencimento_picker.set_date(self.projeto.data_vencimento)

        # Estado
        estado_map = {
            EstadoProjeto.ATIVO: "Ativo",
            EstadoProjeto.FINALIZADO: "Finalizado",
            EstadoProjeto.PAGO: "Pago",
            EstadoProjeto.ANULADO: "Anulado"
        }
        self.estado_dropdown.set(estado_map[self.projeto.estado])

        # Prémios
        if self.projeto.premio_bruno:
            self.premio_bruno_entry.insert(0, str(self.projeto.premio_bruno))
        if self.projeto.premio_rafael:
            self.premio_rafael_entry.insert(0, str(self.projeto.premio_rafael))

        # Nota
        if self.projeto.nota:
            self.nota_entry.insert("1.0", self.projeto.nota)

    def guardar(self):
        """Guarda o projeto"""
        try:
            # Get values
            tipo_str = self.tipo_dropdown.get()
            tipo = TipoProjeto.EMPRESA if tipo_str == "Empresa" else TipoProjeto.PESSOAL
            owner = self.owner_dropdown.get()

            cliente_str = self.cliente_dropdown.get()
            cliente_id = self.clientes_map.get(cliente_str) if cliente_str != "(Nenhum)" else None

            descricao = self.descricao_entry.get("1.0", "end-1c").strip()
            if not descricao:
                messagebox.showerror("Erro", "Descrição é obrigatória")
                return

            valor_str = self.valor_entry.get().strip()
            if not valor_str:
                messagebox.showerror("Erro", "Valor é obrigatório")
                return
            valor = Decimal(valor_str.replace(',', '.'))

            # Datas
            data_inicio = self.periodo_picker.start_date if self.periodo_picker.get() else None
            data_fim = self.periodo_picker.end_date if self.periodo_picker.get() else None
            data_faturacao = self.data_faturacao_picker.get_date() if self.data_faturacao_picker.get() else None
            data_vencimento = self.data_vencimento_picker.get_date() if self.data_vencimento_picker.get() else None

            # Estado
            estado_map = {
                "Ativo": EstadoProjeto.ATIVO,
                "Finalizado": EstadoProjeto.FINALIZADO,
                "Pago": EstadoProjeto.PAGO,
                "Anulado": EstadoProjeto.ANULADO
            }
            estado = estado_map[self.estado_dropdown.get()]

            # Prémios
            premio_bruno = None
            if self.premio_bruno_entry.get():
                premio_bruno = Decimal(self.premio_bruno_entry.get().replace(',', '.'))

            premio_rafael = None
            if self.premio_rafael_entry.get():
                premio_rafael = Decimal(self.premio_rafael_entry.get().replace(',', '.'))

            # Nota
            nota = self.nota_entry.get("1.0", "end-1c").strip() or None

            # Create or update
            if self.projeto_id:
                # Update
                sucesso, erro = self.manager.atualizar(
                    self.projeto_id,
                    tipo=tipo,
                    owner=owner,
                    cliente_id=cliente_id,
                    descricao=descricao,
                    valor_sem_iva=valor,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    data_faturacao=data_faturacao,
                    data_vencimento=data_vencimento,
                    estado=estado,
                    premio_bruno=premio_bruno,
                    premio_rafael=premio_rafael,
                    nota=nota
                )
            else:
                # Create
                sucesso, projeto, erro = self.manager.criar(
                    tipo=tipo,
                    owner=owner,
                    cliente_id=cliente_id,
                    descricao=descricao,
                    valor_sem_iva=valor,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    data_faturacao=data_faturacao,
                    data_vencimento=data_vencimento,
                    estado=estado,
                    premio_bruno=premio_bruno,
                    premio_rafael=premio_rafael,
                    nota=nota
                )

            if sucesso:
                self.voltar()
            else:
                messagebox.showerror("Erro", f"Erro ao guardar: {erro}")

        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def voltar(self):
        """Volta para a lista de projetos"""
        # Navigate back to projetos list
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("projetos")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")

# -*- coding: utf-8 -*-
"""
Tela de Formulário de Despesa - Screen dedicado para criar/editar despesas
Segue mesmo padrão de ui/screens/projeto_form.py
"""
import customtkinter as ctk
from sqlalchemy.orm import Session
from logic.despesas import DespesasManager
from ui.components.date_picker_dropdown import DatePickerDropdown
from database.models import TipoDespesa, EstadoDespesa
from typing import Optional
from datetime import date
from tkinter import messagebox
from decimal import Decimal


class DespesaFormScreen(ctk.CTkFrame):
    """
    Screen para criar/editar despesas

    Navegação via MainWindow.show_screen("despesa_form", despesa_id=None/ID)
    """

    def __init__(self, parent, db_session: Session, despesa_id: Optional[int] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.db_session = db_session
        self.despesa_id = despesa_id
        self.manager = DespesasManager(db_session)

        # Estado
        self.despesa = None
        self.fornecedores_map = {}
        self.projetos_map = {}

        # Configure
        self.configure(fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.create_widgets()

        # Load data se edição
        if despesa_id:
            self.carregar_despesa()

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
        # 2. CAMPOS DA DESPESA
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
        titulo = "Nova Despesa" if not self.despesa_id else "Editar Despesa"
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

        # Tipo
        ctk.CTkLabel(fields_frame, text="Tipo *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8))

        self.tipo_var = ctk.StringVar(value="FIXA_MENSAL")
        tipo_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        tipo_frame.grid(row=1, column=0, sticky="w", pady=(0, 18))

        tipos = [
            ("Fixa Mensal", "FIXA_MENSAL"),
            ("Pessoal BA", "PESSOAL_BRUNO"),
            ("Pessoal RR", "PESSOAL_RAFAEL"),
            ("Equipamento", "EQUIPAMENTO"),
            ("Projeto", "PROJETO")
        ]

        for label, value in tipos:
            ctk.CTkRadioButton(tipo_frame, text=label, variable=self.tipo_var, value=value).pack(side="left", padx=(0, 15))

        # Data
        ctk.CTkLabel(fields_frame, text="Data *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 8))
        self.data_picker = DatePickerDropdown(fields_frame, placeholder="Selecionar data...")
        self.data_picker.grid(row=3, column=0, sticky="ew", pady=(0, 18))

        # Credor/Fornecedor
        ctk.CTkLabel(fields_frame, text="Credor/Fornecedor", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=4, column=0, sticky="w", pady=(0, 8))
        fornecedores = self.manager.obter_fornecedores()
        fornecedor_options = ["(Nenhum)"] + [f"{f.numero} - {f.nome}" for f in fornecedores]
        self.credor_dropdown = ctk.CTkOptionMenu(fields_frame, values=fornecedor_options, width=400, height=35)
        self.credor_dropdown.grid(row=5, column=0, sticky="w", pady=(0, 18))
        self.fornecedores_map = {f"{f.numero} - {f.nome}": f.id for f in fornecedores}

        # Projeto associado
        ctk.CTkLabel(fields_frame, text="Projeto Associado", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=6, column=0, sticky="w", pady=(0, 8))
        projetos = self.manager.obter_projetos()
        projeto_options = ["(Nenhum)"] + [f"{p.numero} - {p.descricao[:30]}" for p in projetos]
        self.projeto_dropdown = ctk.CTkOptionMenu(fields_frame, values=projeto_options, width=400, height=35)
        self.projeto_dropdown.grid(row=7, column=0, sticky="w", pady=(0, 18))
        self.projetos_map = {f"{p.numero} - {p.descricao[:30]}": p.id for p in projetos}

        # Descrição
        ctk.CTkLabel(fields_frame, text="Descrição *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=8, column=0, sticky="w", pady=(0, 8))
        self.descricao_entry = ctk.CTkTextbox(fields_frame, height=90)
        self.descricao_entry.grid(row=9, column=0, sticky="ew", pady=(0, 18))

        # Valores
        valores_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        valores_frame.grid(row=10, column=0, sticky="ew", pady=(0, 18))
        valores_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(valores_frame, text="Valor sem IVA *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 12))
        self.valor_sem_iva_entry = ctk.CTkEntry(valores_frame, placeholder_text="0.00", height=35)
        self.valor_sem_iva_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(8, 0))

        ctk.CTkLabel(valores_frame, text="Valor com IVA *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=1, sticky="w")
        self.valor_com_iva_entry = ctk.CTkEntry(valores_frame, placeholder_text="0.00", height=35)
        self.valor_com_iva_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0))

        # Estado
        ctk.CTkLabel(fields_frame, text="Estado *", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=11, column=0, sticky="w", pady=(0, 8))
        self.estado_dropdown = ctk.CTkOptionMenu(fields_frame, values=["Pendente", "Vencido", "Pago"], height=35)
        self.estado_dropdown.grid(row=12, column=0, sticky="w", pady=(0, 18))

        # Data pagamento
        ctk.CTkLabel(fields_frame, text="Data Pagamento (se pago)", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=13, column=0, sticky="w", pady=(0, 8))
        self.data_pagamento_picker = DatePickerDropdown(fields_frame, placeholder="Selecionar data de pagamento...")
        self.data_pagamento_picker.grid(row=14, column=0, sticky="ew", pady=(0, 18))

        # Nota
        ctk.CTkLabel(fields_frame, text="Nota", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=15, column=0, sticky="w", pady=(0, 8))
        self.nota_entry = ctk.CTkTextbox(fields_frame, height=70)
        self.nota_entry.grid(row=16, column=0, sticky="ew", pady=(0, 10))

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
            fg_color=("#F44336", "#C62828"),
            hover_color=("#E57373", "#B71C1C")
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

    def carregar_despesa(self):
        """Carrega dados da despesa para edição"""
        self.despesa = self.manager.obter_por_id(self.despesa_id)
        if not self.despesa:
            messagebox.showerror("Erro", "Despesa não encontrada!")
            self.voltar()
            return

        # Atualizar título
        self.title_label.configure(text=f"Editar Despesa {self.despesa.numero}")

        d = self.despesa

        # Tipo
        self.tipo_var.set(d.tipo.value)

        # Data
        if d.data:
            self.data_picker.set_date(d.data)

        # Credor
        if d.credor:
            credor_str = f"{d.credor.numero} - {d.credor.nome}"
            self.credor_dropdown.set(credor_str)

        # Projeto
        if d.projeto:
            projeto_str = f"{d.projeto.numero} - {d.projeto.descricao[:30]}"
            self.projeto_dropdown.set(projeto_str)

        # Descrição
        self.descricao_entry.insert("1.0", d.descricao or "")

        # Valores
        self.valor_sem_iva_entry.insert(0, str(d.valor_sem_iva))
        self.valor_com_iva_entry.insert(0, str(d.valor_com_iva))

        # Estado
        estado_map = {
            EstadoDespesa.PENDENTE: "Pendente",
            EstadoDespesa.VENCIDO: "Vencido",
            EstadoDespesa.PAGO: "Pago"
        }
        self.estado_dropdown.set(estado_map[d.estado])

        # Data pagamento
        if d.data_pagamento:
            self.data_pagamento_picker.set_date(d.data_pagamento)

        # Nota
        if d.nota:
            self.nota_entry.insert("1.0", d.nota)

    def guardar(self):
        """Guarda a despesa"""
        try:
            # Get values
            tipo_str = self.tipo_var.get()
            tipo = TipoDespesa[tipo_str]

            if not self.data_picker.get():
                messagebox.showerror("Erro", "Data é obrigatória")
                return
            data_despesa = self.data_picker.get_date()

            credor_str = self.credor_dropdown.get()
            credor_id = self.fornecedores_map.get(credor_str) if credor_str != "(Nenhum)" else None

            projeto_str = self.projeto_dropdown.get()
            projeto_id = self.projetos_map.get(projeto_str) if projeto_str != "(Nenhum)" else None

            descricao = self.descricao_entry.get("1.0", "end-1c").strip()
            if not descricao:
                messagebox.showerror("Erro", "Descrição é obrigatória")
                return

            valor_sem_iva_str = self.valor_sem_iva_entry.get().strip()
            if not valor_sem_iva_str:
                messagebox.showerror("Erro", "Valor sem IVA é obrigatório")
                return
            valor_sem_iva = Decimal(valor_sem_iva_str.replace(',', '.'))

            valor_com_iva_str = self.valor_com_iva_entry.get().strip()
            if not valor_com_iva_str:
                messagebox.showerror("Erro", "Valor com IVA é obrigatório")
                return
            valor_com_iva = Decimal(valor_com_iva_str.replace(',', '.'))

            estado_map = {
                "Pendente": EstadoDespesa.PENDENTE,
                "Vencido": EstadoDespesa.VENCIDO,
                "Pago": EstadoDespesa.PAGO
            }
            estado = estado_map[self.estado_dropdown.get()]

            data_pagamento = None
            if self.data_pagamento_picker.get():
                data_pagamento = self.data_pagamento_picker.get_date()

            nota = self.nota_entry.get("1.0", "end-1c").strip() or None

            # Create or update
            if self.despesa_id:
                sucesso, erro = self.manager.atualizar(
                    self.despesa_id,
                    tipo=tipo,
                    data=data_despesa,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    estado=estado,
                    data_pagamento=data_pagamento,
                    nota=nota
                )
            else:
                sucesso, despesa, erro = self.manager.criar(
                    tipo=tipo,
                    data=data_despesa,
                    descricao=descricao,
                    valor_sem_iva=valor_sem_iva,
                    valor_com_iva=valor_com_iva,
                    credor_id=credor_id,
                    projeto_id=projeto_id,
                    estado=estado,
                    data_pagamento=data_pagamento,
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
        """Volta para a lista de despesas"""
        main_window = self.master.master
        if hasattr(main_window, 'show_screen'):
            main_window.show_screen("despesas")
        else:
            messagebox.showerror("Erro", "Não foi possível navegar de volta")
